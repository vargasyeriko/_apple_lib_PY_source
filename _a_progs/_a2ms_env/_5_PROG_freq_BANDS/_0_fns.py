# -----######-----######-----######-----######-----######-----######-----######-----
#  _0_fns.py  —  LIVE 3-BAND EQ CONSOLE (TEXTUAL + MOUSE SLIDERS)  |  Yeriko / M1
# -----######-----######-----######-----######-----######-----######-----######-----
#  MAIN IMPORTABLE FUNCTION:
#      _audio_0611_textual3band_GET_live_eq_console()
#
#  What it does:
#    • Prompts for an AIFF file path (terminal)
#    • Plays it out in real time
#    • Splits into 3 bands (LR4 @ 120 Hz / 4 kHz): Low / Mid / High
#    • Mouse-draggable faders for Low / Mid / High gains (±12 dB, 0.5 dB steps)
#    • Master volume (-24…+6 dB, 0.5 dB steps)
#    • Latency control (blocksize 64…1024, live apply)
#    • TQM bar (health), XRuns, CPU ms, Clip latch, Peak meters
#
#  Deps (install in your 2ms_env):
#      pip install numpy scipy sounddevice soundfile textual textual-slider
#
#  Notes:
#    • Textual core has no Slider; we use the plugin `textual-slider` (integer-only).
#    • We map 1 slider step = 0.5 dB; blocksize slider is in frames.
#    • Latency changes trigger a seamless stream restart with the new blocksize.
# -----######-----######-----######-----######-----######-----######-----######-----

import time
import threading
import numpy as np
import sounddevice as sd
import soundfile as sf
from scipy.signal import butter, sosfilt

# Textual (UI)
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Label, Button, ProgressBar
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive

# Mouse-enabled sliders (plugin)
from textual_slider import Slider  # pip install textual-slider


# =============================== DSP HELPERS ===============================

def _db_to_lin(db):
    return 10.0 ** (db / 20.0)

def _design_lr4_crossovers(fs, f_lo=120.0, f_hi=4000.0):
    """
    Design LR4 (24 dB/oct) crossovers as cascaded 2nd-order Butterworth filters.
    Returns dict with SOS arrays for:
      - 'lp_lo' (low-pass @ f_lo), 'hp_hi' (high-pass @ f_hi),
      - 'mid_hp' (high-pass @ f_lo), 'mid_lp' (low-pass @ f_hi)
    """
    def _butter_sos(kind, fc):
        wc = fc / (fs * 0.5)
        return butter(2, wc, btype=kind, output='sos')

    sos_lp_lo = np.vstack([_butter_sos('low',  f_lo),
                           _butter_sos('low',  f_lo)])
    sos_hp_hi = np.vstack([_butter_sos('high', f_hi),
                           _butter_sos('high', f_hi)])

    sos_mid_hp = np.vstack([_butter_sos('high', f_lo),
                            _butter_sos('high', f_lo)])
    sos_mid_lp = np.vstack([_butter_sos('low',  f_hi),
                            _butter_sos('low',  f_hi)])

    return {'lp_lo': sos_lp_lo, 'hp_hi': sos_hp_hi, 'mid_hp': sos_mid_hp, 'mid_lp': sos_mid_lp}

def _alloc_zi(sos):
    # Allocate zi for sosfilt per section, per channel (L/R)
    return np.zeros((sos.shape[0], 2), dtype=np.float32)


# =============================== AUDIO ENGINE ===============================

class _ThreeBandEngine:
    """Streams an AIFF file, splits into 3 bands (LR4), applies per-band + master gains."""

    def __init__(self, path, blocksize=256):
        self.path = path
        self.blocksize = int(blocksize)

        # Shared realtime params
        self.gain_low_db  = 0.0
        self.gain_mid_db  = 0.0
        self.gain_high_db = 0.0
        self.master_db    = 0.0

        # IO / state
        self.file = None
        self.stream = None
        self.fs = 44100
        self.channels = 2
        self.finished = False
        self.restart_flag = False

        # Health / meters
        self.blocks_processed = 0
        self.blocks_expected = 0
        self.xruns = 0
        self.clip_latch = False
        self.cpu_avg_ms = 0.0
        self.peak_hold = np.array([0.0, 0.0], dtype=np.float32)

        # Crossovers
        self.crossover_lo = 120.0
        self.crossover_hi = 4000.0
        self.sos = {}
        self.z = {}

        self._lock = threading.Lock()

    # ------------- File & filters -------------

    def _open_file(self):
        self.file = sf.SoundFile(self.path, mode='r')
        self.fs = int(self.file.samplerate)
        self.channels = int(self.file.channels)
        if self.channels < 1:
            raise RuntimeError("Unsupported channel count.")
        self._init_filters()

    def _init_filters(self):
        self.sos = _design_lr4_crossovers(self.fs, self.crossover_lo, self.crossover_hi)
        self._init_states()

    def _init_states(self):
        self.z = {
            'lp_L':  _alloc_zi(self.sos['lp_lo']),
            'lp_R':  _alloc_zi(self.sos['lp_lo']),
            'hp_L':  _alloc_zi(self.sos['hp_hi']),
            'hp_R':  _alloc_zi(self.sos['hp_hi']),
            'mhp_L': _alloc_zi(self.sos['mid_hp']),
            'mhp_R': _alloc_zi(self.sos['mid_hp']),
            'mlp_L': _alloc_zi(self.sos['mid_lp']),
            'mlp_R': _alloc_zi(self.sos['mid_lp']),
        }

    # ------------- Public param setters -------------

    def set_blocksize(self, new_bs):
        with self._lock:
            self.blocksize = int(new_bs)
            self.restart_flag = True

    def set_gains(self, low=None, mid=None, high=None, master=None):
        with self._lock:
            if low    is not None: self.gain_low_db  = float(low)
            if mid    is not None: self.gain_mid_db  = float(mid)
            if high   is not None: self.gain_high_db = float(high)
            if master is not None: self.master_db    = float(master)

    # ------------- Core processing -------------

    def _split_3way(self, x):
        """Split stereo x (F,2) into (low, mid, high), each (F,2)"""
        # per-channel filter with persistent zi per SOS section
        def filt_pair(xL, xR, sos, zL_key, zR_key):
            yL, self.z[zL_key] = sosfilt(sos, xL, zi=self.z[zL_key])
            yR, self.z[zR_key] = sosfilt(sos, xR, zi=self.z[zR_key])
            return yL, yR

        # Low: LP @ f_lo
        L_l, R_l = filt_pair(x[:, 0], x[:, 1], self.sos['lp_lo'],  'lp_L',  'lp_R')

        # High: HP @ f_hi
        L_h, R_h = filt_pair(x[:, 0], x[:, 1], self.sos['hp_hi'],  'hp_L',  'hp_R')

        # Mid: HP(f_lo) then LP(f_hi)
        L_m, R_m = filt_pair(x[:, 0], x[:, 1], self.sos['mid_hp'], 'mhp_L', 'mhp_R')
        L_m, R_m = filt_pair(L_m,     R_m,     self.sos['mid_lp'], 'mlp_L', 'mlp_R')

        low  = np.stack([L_l, R_l], axis=1)
        mid  = np.stack([L_m, R_m], axis=1)
        high = np.stack([L_h, R_h], axis=1)
        return low, mid, high

    def _callback(self, outdata, frames, time_info, status):
        t0 = time.perf_counter()
        if status:
            if getattr(status, "output_underflow", False) or getattr(status, "input_overflow", False):
                self.xruns += 1

        # Read from file
        data = self.file.read(frames, dtype='float32', always_2d=True)
        if data.shape[0] < frames:
            # pad end
            pad = np.zeros((frames - data.shape[0], data.shape[1]), dtype=np.float32)
            data = np.vstack([data, pad])
            self.finished = True

        # Ensure stereo
        if data.shape[1] == 1:
            data = np.repeat(data, 2, axis=1)

        # Split into bands
        low, mid, high = self._split_3way(data)

        # Gains (atomic read)
        with self._lock:
            gl = _db_to_lin(self.gain_low_db)
            gm = _db_to_lin(self.gain_mid_db)
            gh = _db_to_lin(self.gain_high_db)
            gM = _db_to_lin(self.master_db)

        y = (low * gl) + (mid * gm) + (high * gh)
        y *= gM

        # Metering
        peaks = np.max(np.abs(y), axis=0)
        self.peak_hold = np.maximum(self.peak_hold * 0.95, peaks)
        if np.any(peaks > 0.999):
            self.clip_latch = True

        outdata[:] = y
        self.blocks_processed += 1

        # CPU timing (EMA)
        dt_ms = (time.perf_counter() - t0) * 1000.0
        self.cpu_avg_ms = 0.9 * self.cpu_avg_ms + 0.1 * dt_ms

    def _run_once(self):
        # Reset counters / meters
        self.blocks_processed = 0
        self.blocks_expected  = 0
        self.xruns = 0
        self.clip_latch = False
        self.cpu_avg_ms = 0.0
        self.peak_hold[:] = 0.0
        self.file.seek(0)
        self.finished = False

        bs = int(self.blocksize)
        with sd.OutputStream(channels=2, samplerate=self.fs, blocksize=bs,
                             dtype='float32', callback=self._callback):
            t0 = time.perf_counter()
            while not self.finished and not self.restart_flag:
                time.sleep(0.05)
                elapsed = time.perf_counter() - t0
                # expected blocks = elapsed * (fs / blocksize)
                self.blocks_expected = int(elapsed * (self.fs / bs))
            time.sleep(0.05)  # drain a bit

    def run(self):
        self._open_file()
        while True:
            self._run_once()
            if self.restart_flag:
                with self._lock:
                    self.restart_flag = False
                # re-init filter states for clean restart
                self._init_states()
                continue
            break


# =============================== TEXTUAL UI ===============================

class _EQPanel(Static):
    # Reactive state (mirrors engine for UI labels)
    low = reactive(0.0)
    mid = reactive(0.0)
    high = reactive(0.0)
    master = reactive(0.0)
    blocksize = reactive(256)
    fs_label = reactive("44.1 kHz")
    health = reactive(0)
    xruns = reactive(0)
    clip = reactive(False)
    cpu_ms = reactive(0.0)

    def __init__(self, engine: _ThreeBandEngine):
        super().__init__()
        self.engine = engine
        self._timer = None

        # Sliders
        self.s_low = None
        self.s_mid = None
        self.s_high = None
        self.s_master = None
        self.s_bs = None

        # Labels / widgets
        self.lbl_fs = None
        self.lbl_peaks = None
        self.pb = None
        self.lbl_health = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical():
            yield Label("MULTIBAND LIVE CONSOLE — 3-Band (LR4) | Mouse: drag sliders | Click 'Apply Latency'")
            with Horizontal():
                with Vertical():
                    yield Label("Low Gain (dB, ±12 / 0.5 step)")
                    self.s_low = Slider(min=-24, max=24, step=1, value=0)
                    yield self.s_low
                    self.lbl_low = Label("Low: +0.0 dB")
                    yield self.lbl_low
                with Vertical():
                    yield Label("Mid Gain (dB, ±12 / 0.5 step)")
                    self.s_mid = Slider(min=-24, max=24, step=1, value=0)
                    yield self.s_mid
                    self.lbl_mid = Label("Mid: +0.0 dB")
                    yield self.lbl_mid
                with Vertical():
                    yield Label("High Gain (dB, ±12 / 0.5 step)")
                    self.s_high = Slider(min=-24, max=24, step=1, value=0)
                    yield self.s_high
                    self.lbl_high = Label("High: +0.0 dB")
                    yield self.lbl_high
                with Vertical():
                    yield Label("Master (dB, -24…+6 / 0.5 step)")
                    self.s_master = Slider(min=-48, max=12, step=1, value=0)
                    yield self.s_master
                    self.lbl_master = Label("Master: +0.0 dB")
                    yield self.lbl_master
            with Horizontal():
                with Vertical():
                    yield Label("Latency / Blocksize (frames)")
                    self.s_bs = Slider(min=64, max=1024, step=64, value=256)
                    yield self.s_bs
                    yield Button("Apply Latency", id="apply_latency")
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
        # UI refresh timer (~20 FPS)
        self._timer = self.set_interval(0.05, self._tick)

    # Button handler (Textual 6.x)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "apply_latency":
            self.engine.set_blocksize(int(self.s_bs.value))

    def _tick(self):
        # Update SR label
        self.lbl_fs.update(f"Sample Rate: {self.engine.fs/1000.0:.1f} kHz")

        # Map integer sliders → dB (0.5 dB per step)
        v_low_db    = self.s_low.value    / 2.0
        v_mid_db    = self.s_mid.value    / 2.0
        v_high_db   = self.s_high.value   / 2.0
        v_master_db = self.s_master.value / 2.0

        # Push to engine only when changed
        if v_low_db != self.low:
            self.low = v_low_db
            self.engine.set_gains(low=v_low_db)
        if v_mid_db != self.mid:
            self.mid = v_mid_db
            self.engine.set_gains(mid=v_mid_db)
        if v_high_db != self.high:
            self.high = v_high_db
            self.engine.set_gains(high=v_high_db)
        if v_master_db != self.master:
            self.master = v_master_db
            self.engine.set_gains(master=v_master_db)

        # Update small value labels
        self.lbl_low.update(   f"Low:   {self.low:+.1f} dB")
        self.lbl_mid.update(   f"Mid:   {self.mid:+.1f} dB")
        self.lbl_high.update(  f"High:  {self.high:+.1f} dB")
        self.lbl_master.update(f"Master:{self.master:+.1f} dB")

        # Latency slider mirrors (applied on button)
        self.blocksize = int(self.s_bs.value)

        # TQM / peaks / health
        exp = max(1, self.engine.blocks_expected)
        got = self.engine.blocks_processed
        health = int(100 * min(1.0, got / exp)) if exp else 0
        # Textual 6.x: set property or use update(progress=health)
        self.pb.progress = health

        pkL, pkR = self.engine.peak_hold
        self.lbl_peaks.update(f"Peaks: L {pkL:0.2f}  R {pkR:0.2f}")

        self.xruns = self.engine.xruns
        self.clip = self.engine.clip_latch
        self.cpu_ms = self.engine.cpu_avg_ms
        self.lbl_health.update(
            f"Health: {health}% | XRuns: {self.xruns} | Clip: {self.clip} | CPU: {self.cpu_ms:0.2f} ms"
        )


class _EQApp(App):
    CSS = """
    Screen { layout: vertical; }
    Slider { width: 40; }
    ProgressBar { width: 60; }
    """

    def __init__(self, engine: _ThreeBandEngine):
        super().__init__()
        self.engine = engine
        self._audio_thread = None

    def compose(self) -> ComposeResult:
        yield _EQPanel(self.engine)

    def on_mount(self):
        # Run audio engine in a separate thread so UI stays responsive
        self._audio_thread = threading.Thread(target=self.engine.run, daemon=True)
        self._audio_thread.start()


# =============================== PUBLIC ENTRY ===============================

def _audio_0611_textual3band_GET_live_eq_console():
    """
    -----######----- CORE FUNCTION: LIVE 3-BAND EQ CONSOLE (TEXTUAL) -----######-----
    Asks for an AIFF file path, then launches a mouse-enabled terminal UI
    with 3-band LR4 crossover, per-band faders, Master volume, latency control,
    and a TQM bar.
    """
    aiff_path = input("Enter AIFF file path: ").strip()
    # Normalize quotes/extra spaces you might paste
    aiff_path = aiff_path.strip().strip("'").strip('"')
    if not aiff_path:
        print("No path provided. Exiting.")
        return

    try:
        with sf.SoundFile(aiff_path, 'r') as _:
            pass
    except Exception as e:
        print(f"Error opening file: {e}")
        return

    engine = _ThreeBandEngine(aiff_path, blocksize=256)
    app = _EQApp(engine)
    app.run()
