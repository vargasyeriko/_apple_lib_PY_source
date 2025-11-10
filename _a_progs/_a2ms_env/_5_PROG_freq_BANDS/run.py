# -----######-----######  CORE IMPORTABLE FUNCTION  -----######-----######
# _ui_0611_audioengine_GET_realtime
#
# Params:
#   audio_path (string): path to WAV/AIFF/FLAC
#   params (dict): shared dict the UI will update in real-time
#                  keys: {'gain_db','low_db','mid_db','high_db'}
#   sr_target (int): stream sample rate (macOS device rate)
#   blocksize (int): audio callback blocksize
#   device (int/str/None): sounddevice device id or name
#
# Behavior:
#   - Streams audio through a low-latency callback
#   - Applies headroom, 3-band light EQ, smoothing, and safety limiter
#   - Prints a TQM bar (CPU/peak) periodically in main thread
#   - Returns when playback ends or KeyboardInterrupt
# ----------------------------------------------------------------------

import time, sys, threading, queue, math
import numpy as np

try:
    import sounddevice as sd
    import soundfile as sf
except ImportError:
    raise RuntimeError("Please pip install sounddevice soundfile")

def _db_to_lin(db):
    return 10.0 ** (db / 20.0)

def _one_pole_smoother(prev, target, alpha):
    # alpha in (0,1], smaller = smoother
    return prev + alpha * (target - prev)

def _design_shelving(fc, sr, gain_db, shelf_type="low"):
    # Simple 1st-order shelving (one-pole). Returns (a0,a1,b1) for direct form:
    # y[n] = a0*x[n] + a1*x[n-1] - b1*y[n-1]
    # Lightweight & stable for small EQ moves; good for live tweaking.
    g = _db_to_lin(gain_db)
    # Pre-warp
    x = math.exp(-2.0*math.pi*fc/sr)
    if shelf_type == "low":
        a0 = (1.0 - x) * g
        a1 = 0.0
        b1 = -x
    elif shelf_type == "high":
        a0 = (1.0 - x)
        a1 = 0.0
        b1 = -x * (1.0/g)
        # Normalize overall gain at DC ~1 for small boosts/cuts
    else:
        # Mid = simple wide bell via two shelves blend (very light hack)
        # You can replace with a biquad peaking filter later.
        a0 = (1.0 - x) * g
        a1 = 0.0
        b1 = -x
    return a0, a1, b1

class _OnePoleFilter:
    def __init__(self, fc, sr, gain_db, shelf_type):
        self.a0, self.a1, self.b1 = _design_shelving(fc, sr, gain_db, shelf_type)
        self.x1L = 0.0; self.y1L = 0.0
        self.x1R = 0.0; self.y1R = 0.0
        self.fc = fc; self.shelf_type = shelf_type
        self.sr = sr
        self.gain_db = gain_db

    def update_gain(self, gain_db):
        if abs(gain_db - self.gain_db) < 0.05:
            return
        self.gain_db = gain_db
        self.a0, self.a1, self.b1 = _design_shelving(self.fc, self.sr, self.gain_db, self.shelf_type)

    def process(self, x):
        # x: (N, C) float32
        if x.ndim == 1:
            x = x[:, None]
        y = np.empty_like(x)
        # Stereo or mono-safe
        for ch in range(x.shape[1]):
            x1 = self.x1L if ch == 0 else self.x1R
            y1 = self.y1L if ch == 0 else self.y1R
            out = np.empty(x.shape[0], dtype=x.dtype)
            a0, a1, b1 = self.a0, self.a1, self.b1
            for n in range(x.shape[0]):
                xn = x[n, ch]
                yn = a0*xn + a1*x1 - b1*y1
                out[n] = yn
                x1 = xn
                y1 = yn
            if ch == 0:
                self.x1L, self.y1L = x1, y1
            else:
                self.x1R, self.y1R = x1, y1
            y[:, ch] = out
        return y

def _safety_limiter(buf, ceiling_lin=0.98):
    peak = np.max(np.abs(buf))
    if peak <= ceiling_lin:
        return buf, peak
    # Simple hard-knee scaler (not a brickwall but prevents explosions)
    scale = ceiling_lin / (peak + 1e-12)
    return buf * scale, peak

def _read_blocks(audio_path, sr_target, blocksize):
    f = sf.SoundFile(audio_path, mode='r')
    src_sr = f.samplerate
    ch = f.channels
    if src_sr != sr_target:
        # Let sounddevice handle SR conversion by reporting intended samplerate to stream.
        # Alternatively, implement high-quality resampling here (e.g. samplerate, resampy).
        pass
    while True:
        data = f.read(blocksize, dtype='float32', always_2d=True)
        if len(data) == 0:
            break
        yield data
    f.close()

def _ui_0611_audioengine_GET_realtime(audio_path, params, sr_target=44100, blocksize=512, device=None):
    """
    -----######-----######  CORE IMPORTABLE FUNCTION  -----######-----######
    """
    # Defaults if missing
    for k, v in [('gain_db', 0.0), ('low_db', 0.0), ('mid_db', 0.0), ('high_db', 0.0)]:
        params.setdefault(k, v)

    # Smoothing state
    sm_gain = params['gain_db']
    sm_low  = params['low_db']
    sm_mid  = params['mid_db']
    sm_high = params['high_db']
    alpha = 0.05  # smaller = smoother

    # Filters
    low = _OnePoleFilter(fc=180.0,  sr=sr_target, gain_db=sm_low,  shelf_type="low")
    mid = _OnePoleFilter(fc=1000.0, sr=sr_target, gain_db=sm_mid,  shelf_type="mid")
    hig = _OnePoleFilter(fc=6000.0, sr=sr_target, gain_db=sm_high, shelf_type="high")

    q_frames = queue.Queue(maxsize=8)
    peak_meter = {'value': 0.0}
    xruns = {'count': 0}
    done = {'flag': False}

    # Producer thread: file reader
    def _reader():
        try:
            for blk in _read_blocks(audio_path, sr_target, blocksize):
                try:
                    q_frames.put(blk, timeout=1.0)
                except queue.Full:
                    # If UI stalls, drop (avoid blocking file read forever)
                    pass
        finally:
            done['flag'] = True

    th = threading.Thread(target=_reader, daemon=True)
    th.start()

    # Audio callback
    def _callback(outdata, frames, time_info, status):
        if status.output_underflow or status.input_underflow:
            xruns['count'] += 1
        try:
            blk = q_frames.get_nowait()
        except queue.Empty:
            outdata.fill(0.0)
            return

        # Smooth params
        sm_gain = _one_pole_smoother(_callback.sm_gain, params.get('gain_db', 0.0), alpha)
        sm_low  = _one_pole_smoother(_callback.sm_low,  params.get('low_db',  0.0), alpha)
        sm_mid  = _one_pole_smoother(_callback.sm_mid,  params.get('mid_db',  0.0), alpha)
        sm_high = _one_pole_smoother(_callback.sm_high, params.get('high_db', 0.0), alpha)
        _callback.sm_gain, _callback.sm_low, _callback.sm_mid, _callback.sm_high = sm_gain, sm_low, sm_mid, sm_high

        # Update filters if needed
        low.update_gain(sm_low)
        mid.update_gain(sm_mid)
        hig.update_gain(sm_high)

        # Headroom
        headroom = _db_to_lin(-9.0)
        y = blk * headroom

        # EQ (very light, cheap)
        y = low.process(y)
        y = mid.process(y)
        y = hig.process(y)

        # Master gain
        y *= _db_to_lin(sm_gain)

        # Safety limiter
        y, pk = _safety_limiter(y, ceiling_lin=0.98)
        peak_meter['value'] = 0.9*peak_meter['value'] + 0.1*float(pk)

        # Fit channels to outdata
        if y.shape[1] < outdata.shape[1]:
            # mono->stereo
            y = np.repeat(y, outdata.shape[1], axis=1)
        elif y.shape[1] > outdata.shape[1]:
            y = y[:, :outdata.shape[1]]

        outdata[:] = y

    _callback.sm_gain = sm_gain
    _callback.sm_low  = sm_low
    _callback.sm_mid  = sm_mid
    _callback.sm_high = sm_high

    stream = sd.OutputStream(
        samplerate=sr_target,
        blocksize=blocksize,
        channels=2,
        dtype='float32',
        device=device,
        callback=_callback,
        latency='low'
    )

    # TQM bar (non-audio thread)
    def _tqm():
        while not done['flag'] or not q_frames.empty():
            pk = peak_meter['value']
            xrun = xruns['count']
            bars = int(min(50, max(0, pk*55)))
            sys.stdout.write(
                f"\rTQM | Peak: [{'#'*bars}{'-'*(50-bars)}] {pk:0.3f} | XRuns: {xrun}      "
            )
            sys.stdout.flush()
            time.sleep(0.2)
        print("\nTQM | Done.")

    tqm_thread = threading.Thread(target=_tqm, daemon=True)
    tqm_thread.start()

    # Start stream
    with stream:
        try:
            while not done['flag'] or not q_frames.empty():
                time.sleep(0.01)
        except KeyboardInterrupt:
            pass
################### run 

# Example usage (wire your UI to update `params` in real-time)
from pathlib import Path

audio_path = "/Users/yerik/Downloads/___Delete_analyze again /try.aiff"  # your file
params = {
    'gain_db': 0.0,
    'low_db':  0.0,
    'mid_db':  0.0,
    'high_db': 0.0,
}

# Keep the process awake & un-throttled on macOS (run your script via caffeinate):
#   caffeinate -dimsu python this_script.py
_ui_0611_audioengine_GET_realtime(audio_path, params, sr_target=44100, blocksize=512, device=None)

# You can update parameters from ANY thread, e.g.:
# params['gain_db'] = -3.0
# params['low_db']  = +2.0
# params['mid_db']  = -1.5
# params['high_db'] = +1.0
