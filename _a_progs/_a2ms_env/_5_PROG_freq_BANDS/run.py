# -----######-----######-----######-----######-----######-----######-----######-----
#  MAIN IMPORTABLE FUNCTION (with TQM bar + Textual mouse sliders)
# -----######-----######-----######-----######-----######-----######-----######-----
# Deps:
#   pip install numpy scipy sounddevice soundfile textual textual-slider
#
# Notes:
#   - Best in macOS Terminal/iTerm2 with mouse enabled.
#   - Works with stereo/mono AIFF (mono is upmixed).
#   - Blocksize slider restarts stream smoothly.
# -----######-----######-----######-----######-----######-----######-----######-----

import time, threading
import numpy as np
import sounddevice as sd
import soundfile as sf
from scipy.signal import butter, sosfilt

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Label, Button, ProgressBar   # <— no Slider here
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual_slider import Slider  # <— slider plugin

# ======================= DSP: LR4 3-WAY CROSSOVER =======================

def _lr4_bank(fs, f_lo=120.0, f_hi=4000.0):
    def _sos(ftype, fc):
        return butter(2, fc/(fs*0.5), btype=ftype, output='sos')
    bank = {
        "lp_lo": np.vstack([_sos('low',  f_lo), _sos('low',  f_lo)]),
        "hp_hi": np.vstack([_sos('high', f_hi), _sos('high', f_hi)]),
        "mid_hp":np.vstack([_sos('high', f_lo), _sos('high', f_lo)]),
        "mid_lp":np.vstack([_sos('low',  f_hi), _sos('low',  f_hi)]),
    }
    return bank

def _db_to_lin(db):
    return 10.0**(db/20.0)

# ======================= AUDIO ENGINE =======================

class _ThreeBandEngine:
    def __init__(self, path, blocksize=256, f_lo=120.0, f_hi=4000.0):
        self.path = path
        self.blocksize = int(blocksize)
        self.f_lo, self.f_hi = float(f_lo), float(f_hi)

        self.file = None
        self.fs = 44100
        self.channels = 2

        self.gain_low_db = 0.0
        self.gain_mid_db = 0.0
        self.gain_high_db= 0.0
        self.master_db   = 0.0

        self.bank = None
        self.state = {}

        self.blocks_processed = 0
        self.blocks_expected  = 0
        self.xruns = 0
        self.clip_latch = False
        self.cpu_ms = 0.0
        self.peak_hold = np.array([0.0, 0.0], dtype=np.float32)

        self.finished = False
        self.restart_flag = False
        self._lock = threading.Lock()

    def _open(self):
        self.file = sf.SoundFile(self.path, mode="r")
        self.fs = self.file.samplerate
        self.channels = self.file.channels
        self.bank = _lr4_bank(self.fs, self.f_lo, self.f_hi)
        self._init_state()

    def _init_state(self):
        def z(sos): return np.zeros((sos.shape[0], 2), dtype=np.float32)
        self.state = {
            "z_lp_L": z(self.bank["lp_lo"]),  "z_lp_R": z(self.bank["lp_lo"]),
            "z_hp_L": z(self.bank["hp_hi"]),  "z_hp_R": z(self.bank["hp_hi"]),
            "z_mh_L": z(self.bank["mid_hp"]), "z_mh_R": z(self.bank["mid_hp"]),
            "z_ml_L": z(self.bank["mid_lp"]), "z_ml_R": z(self.bank["mid_lp"]),
        }

    def set_blocksize(self, bs):
        with self._lock:
            self.blocksize = int(bs)
            self.restart_flag = True

    def set_gains(self, low=None, mid=None, high=None, master=None):
        with self._lock:
            if low    is not None: self.gain_low_db   = float(low)
            if mid    is not None: self.gain_mid_db   = float(mid)
            if high   is not None: self.gain_high_db  = float(high)
            if master is not None: self.master_db     = float(master)

    def _split(self, x):
        # x: (frames,2)
        def filt(xch, sos, k):
            z = self.state[k]
            y, z_out = sosfilt(sos, xch, zi=z)
            self.state[k] = z_out
            return y
        L = x[:,0]; R = x[:,1]

        lowL = filt(L, self.bank["lp_lo"], "z_lp_L")
        lowR = filt(R, self.bank["lp_lo"], "z_lp_R")

        hiL  = filt(L, self.bank["hp_hi"], "z_hp_L")
        hiR  = filt(R, self.bank["hp_hi"], "z_hp_R")

        midL = filt(L, self.bank["mid_hp"], "z_mh_L")
        midL = filt(midL, self.bank["mid_lp"], "z_ml_L")
        midR = filt(R, self.bank["mid_hp"], "z_mh_R")
        midR = filt(midR, self.bank["mid_lp"], "z_ml_R")

        low = np.stack([lowL, lowR], axis=1)
        mid = np.stack([midL, midR], axis=1)
        hi  = np.stack([hiL,  hiR ], axis=1)
        return low, mid, hi

    def _callback(self, outdata, frames, time_info, status):
        t0 = time.perf_counter()
        if status and (status.input_overflow or status.output_underflow):
            self.xruns += 1

        data = self.file.read(frames, dtype="float32", always_2d=True)
        if data.shape[0] < frames:
            pad = np.zeros((frames - data.shape[0], data.shape[1]), dtype=np.float32)
            data = np.vstack([data, pad])
            self.finished = True

        if data.shape[1] == 1:
            data = np.repeat(data, 2, axis=1)

        low, mid, hi = self._split(data)

        with self._lock:
            gl = _db_to_lin(self.gain_low_db)
            gm = _db_to_lin(self.gain_mid_db)
            gh = _db_to_lin(self.gain_high_db)
            gM = _db_to_lin(self.master_db)

        y = (low*gl) + (mid*gm) + (hi*gh)
        y *= gM

        peaks = np.max(np.abs(y), axis=0)
        self.peak_hold = np.maximum(self.peak_hold*0.95, peaks)
        if np.any(peaks > 0.999):
            self.clip_latch = True

        outdata[:] = y
        self.blocks_processed += 1

        dt = (time.perf_counter() - t0) * 1000.0
        self.cpu_ms = 0.9*self.cpu_ms + 0.1*dt

    def _run_once(self):
        self.blocks_processed = 0
        self.blocks_expected  = 0
        self.xruns = 0
        self.clip_latch = False
        self.cpu_ms = 0.0
        self.peak_hold[:] = 0.0
        self.file.seek(0)
        self.finished = False

        bs = self.blocksize
        with sd.OutputStream(channels=2, samplerate=self.fs, blocksize=bs,
                             dtype='float32', callback=self._callback):
            t0 = time.perf_counter()
            while not self.finished and not self.restart_flag:
                time.sleep(0.05)
                elapsed = time.perf_counter() - t0
                est_blocks = int(elapsed * (self.fs / bs))
                self.blocks_expected = max(self.blocks_expected, est_blocks)
            time.sleep(0.05)

    def run(self):
        self._open()
        while True:
            self._run_once()
            if self.restart_flag:
                with self._lock:
                    self.restart_flag = False
                self._init_state()
                continue
            break

# ======================= TEXTUAL UI =======================

class _EQPanel(Vertical):
    low = reactive(0.0); mid = reactive(0.0); high = reactive(0.0); master = reactive(0.0)
    blocksize = reactive(256)

    def __init__(self, engine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical():
            yield Label("LIVE 3-Band Console — LR4 | Mouse-drag sliders | Click to apply latency")
            with Horizontal():
                with Vertical():
                    yield Label("Low (dB)")
                    self.s_low = Slider(-12, 12, step=0.5, value=0.0, show_value=True)
                    yield self.s_low
                with Vertical():
                    yield Label("Mid (dB)")
                    self.s_mid = Slider(-12, 12, step=0.5, value=0.0, show_value=True)
                    yield self.s_mid
                with Vertical():
                    yield Label("High (dB)")
                    self.s_high = Slider(-12, 12, step=0.5, value=0.0, show_value=True)
                    yield self.s_high
                with Vertical():
                    yield Label("Master (dB)")
                    self.s_master = Slider(-24, 6, step=0.5, value=0.0, show_value=True)
                    yield self.s_master
            with Horizontal():
                with Vertical():
                    yield Label("Latency / Blocksize")
                    self.s_bs = Slider(64, 1024, step=64, value=256, show_value=True)
                    yield self.s_bs
                    self.btn_apply = Button("Apply Latency", id="apply")
                    yield self.btn_apply
                with Vertical():
                    self.lbl_fs = Label("Sample Rate: —")
                    yield self.lbl_fs
                    self.lbl_peaks = Label("Peaks: L 0.00  R 0.00")
                    yield self.lbl_peaks
                with Vertical():
                    yield Label("TQM (Engine Health)")
                    self.pb = ProgressBar(total=100)
                    yield self.pb
                    self.lbl_health = Label("Health: 0% | XRuns: 0 | Clip: False | CPU: 0.00 ms")
                    yield self.lbl_health
        yield Footer()

    def on_mount(self):
        self.set_interval(0.05, self._tick)
        self.s_low.changed.connect(lambda v: self._set_gain("low", v))
        self.s_mid.changed.connect(lambda v: self._set_gain("mid", v))
        self.s_high.changed.connect(lambda v: self._set_gain("high", v))
        self.s_master.changed.connect(lambda v: self._set_gain("master", v))
        self.s_bs.changed.connect(lambda v: setattr(self, "blocksize", int(v)))
        self.btn_apply.on_click = lambda: self.engine.set_blocksize(self.blocksize)

    def _set_gain(self, which, value):
        if   which == "low":    self.engine.set_gains(low=value)
        elif which == "mid":    self.engine.set_gains(mid=value)
        elif which == "high":   self.engine.set_gains(high=value)
        elif which == "master": self.engine.set_gains(master=value)

    def _tick(self):
        fs_k = f"{self.engine.fs/1000:.1f} kHz"
        self.lbl_fs.update(f"Sample Rate: {fs_k}")

        exp = max(1, self.engine.blocks_expected)
        got = self.engine.blocks_processed
        health = int(100 * min(1.0, got/exp))
        self.pb.update(health)

        pkL, pkR = self.engine.peak_hold
        self.lbl_peaks.update(f"Peaks: L {pkL:0.2f}  R {pkR:0.2f}")
        self.lbl_health.update(
            f"Health: {health}% | XRuns: {self.engine.xruns} | Clip: {self.engine.clip_latch} | CPU: {self.engine.cpu_ms:0.2f} ms"
        )

class _EQApp(App):
    CSS = "Slider { width: 36; } ProgressBar { width: 60; }"
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
    def compose(self) -> ComposeResult:
        yield _EQPanel(self.engine)
    def on_mount(self):
        threading.Thread(target=self.engine.run, daemon=True).start()

# ======================= PUBLIC ENTRY =======================

def _audio_0611_textual3band_GET_live_eq_console():
    """
    -----######----- CORE FUNCTION: LIVE 3-BAND EQ CONSOLE (TEXTUAL) -----######-----
    Prompts for an AIFF path, then launches a mouse-enabled terminal UI with:
    - LR4 3-band split (Low/Mid/High)
    - Per-band gain + Master
    - Blocksize (latency) control
    - TQM bar (blocks in-time %, XRuns, clip, CPU)
    """
    aiff_path = input("Enter AIFF file path: ").strip()
    if not aiff_path:
        print("No path provided. Exiting."); return
    try:
        with sf.SoundFile(aiff_path, 'r') as _:
            pass
    except Exception as e:
        print(f"Error opening file: {e}"); return

    engine = _ThreeBandEngine(aiff_path, blocksize=256)
    _EQApp(engine).run()
