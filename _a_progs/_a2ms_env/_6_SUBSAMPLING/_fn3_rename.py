# ===================== 0_FNS =====================
import os
import numpy as np
import soundfile as sf

def _generate_kick(path=""):
    """
    Generate 5 high-quality kick drum one-shots and save them as .wav files.

    Design notes (derived from the attached PDF kick analyses):
    - Duration ~ 0.23 s (≈ 229 ms) for all kicks.
    - Sample rate 44.1 kHz.
    - Normalized just below 0 dBFS (target ≈ -0.35 dBFS).
    - Strong low-end fundamental with a smooth downward pitch bend.
    - Clear transient / click layer.
    - Exponential-style amplitude decay (no abrupt clicks).
    - Slight variation in weight / punch / click between the 5 kicks.
    """

    # ----- safety / path handling -----
    if not path:
        path = os.getcwd()
    os.makedirs(path, exist_ok=True)

    # ----- core constants inferred from the PDF -----
    sr = 44100                      # sample rate (Hz)
    duration = 0.2295               # seconds, ~229 ms as in the stats
    n_samples = int(sr * duration)

    # target peak around -0.35 dBFS (between -0.3 and -0.5)
    target_peak_db = -0.35
    target_peak_lin = 10.0 ** (target_peak_db / 20.0)

    # random generator (for subtle variations in click/noise)
    rng = np.random.default_rng()

    # ------------------------------------------------
    # helper: exponential frequency sweep + body
    # ------------------------------------------------
    def _make_body(f_start, f_end, decay_time, punch_amount):
        """
        Create the low-frequency body of the kick:
        - Exponential downward frequency sweep.
        - Exponential amplitude decay with extra early "punch" boost.
        """
        t = np.arange(n_samples, dtype=np.float64) / sr

        # Exponential frequency trajectory between f_start and f_end
        # f(t) = f_start * (f_end / f_start) ** tau, where tau in [0, 1]
        if n_samples <= 1:
            tau = np.zeros(1, dtype=np.float64)
        else:
            tau = np.linspace(0.0, 1.0, n_samples, endpoint=False)
        freq_t = f_start * (f_end / f_start) ** tau

        # Integrate frequency to phase: phase[n] = 2π * Σ_k (freq[k] / sr)
        phase = 2.0 * np.pi * np.cumsum(freq_t) / sr

        # Base exponential decay envelope
        # decay_time is in seconds (approximate amplitude 1/e at t=decay_time)
        decay_env = np.exp(-t / max(decay_time, 1e-4))

        # Extra punch: a short Gaussian bump near the start
        # Center around 4 ms, width ~3 ms
        punch_center_ms = 4.0
        punch_width_ms = 3.0
        punch_env = np.exp(-0.5 * ((t * 1000.0 - punch_center_ms) / punch_width_ms) ** 2)
        amp_env = decay_env * (1.0 + punch_amount * punch_env)

        body = np.sin(phase) * amp_env
        return body.astype(np.float64)

    # ------------------------------------------------
    # helper: transient / click layer
    # ------------------------------------------------
    def _make_click(click_len_ms, click_level, tilt_hf):
        """
        Create a short high-frequency click using shaped noise.
        - click_len_ms: duration of the click segment in milliseconds.
        - click_level: amplitude scale for the click layer.
        - tilt_hf: emphasize high frequencies via a simple high-pass style operation.
        """
        click_len = max(4, int(sr * click_len_ms / 1000.0))
        t_click = np.arange(click_len, dtype=np.float64) / sr

        # White noise for transient
        noise = rng.standard_normal(click_len)

        # Simple HF emphasis (difference + short moving-average subtraction)
        diff = noise - np.concatenate((noise[:1], noise[:-1]))
        ma_kernel = np.ones(5, dtype=np.float64) / 5.0
        smoothed = np.convolve(noise, ma_kernel, mode="same")
        hf = diff + tilt_hf * (noise - smoothed)

        # Very fast exponential decay
        decay_env = np.exp(-t_click / max(0.002, 1e-4))  # ~2 ms decay
        click = hf * decay_env * click_level

        # Pad to full length of the kick
        out = np.zeros(n_samples, dtype=np.float64)
        out[:click_len] += click
        return out

    # ------------------------------------------------
    # helper: soft saturation to smooth out peaks / add glue
    # ------------------------------------------------
    def _soft_saturate(x, drive):
        """
        Gentle soft clipping using tanh.
        drive > 0: higher values = more saturation.
        """
        if drive <= 0.0:
            return x
        # Normalize slightly before drive to avoid hard clipping
        max_abs = np.max(np.abs(x)) + 1e-12
        x_norm = x / max_abs
        y = np.tanh(x_norm * drive) / np.tanh(drive)
        return y

    # ------------------------------------------------
    # helper: apply fades and final normalization
    # ------------------------------------------------
    def _finalize(x):
        """
        - Remove DC offset.
        - Apply short fade-in / fade-out to avoid clicks.
        - Normalize to the target peak level.
        """
        # Remove DC
        x = x - np.mean(x)

        # Short fades (≈1 ms at start and end)
        fade_len = max(4, int(sr * 0.001))
        fade_in = np.linspace(0.0, 1.0, fade_len, endpoint=True)
        fade_out = fade_in[::-1]

        x[:fade_len] *= fade_in
        x[-fade_len:] *= fade_out

        # Peak normalization
        peak = np.max(np.abs(x)) + 1e-12
        x = x * (target_peak_lin / peak)

        return x.astype(np.float32)

    # ------------------------------------------------
    # per-kick parameter sets (tuned by eye based on PDF stats)
    # ------------------------------------------------
    # Each dict controls:
    # - f_start, f_end : pitch bend range (Hz)
    # - decay_time     : amplitude decay constant (seconds)
    # - punch_amount   : how strong the early punch is
    # - click_len_ms   : click duration in ms
    # - click_level    : relative level of the click layer
    # - tilt_hf        : HF emphasis factor for the click
    # - drive          : soft-saturation amount
    kick_params = [
        # Kick 1: balanced sub & punch, slightly dynamic (cresty)
        dict(f_start=95.0,  f_end=48.0, decay_time=0.165, punch_amount=0.55,
             click_len_ms=5.0,  click_level=0.25, tilt_hf=1.1, drive=1.1),

        # Kick 2: louder / thicker body, shorter decay, more punch
        dict(f_start=105.0, f_end=52.0, decay_time=0.150, punch_amount=0.70,
             click_len_ms=5.0,  click_level=0.30, tilt_hf=1.2, drive=1.3),

        # Kick 3: slightly longer tail, a bit leaner, deeper feel
        dict(f_start=90.0,  f_end=45.0, decay_time=0.180, punch_amount=0.50,
             click_len_ms=6.0,  click_level=0.22, tilt_hf=1.0, drive=1.0),

        # Kick 4: more dynamic (higher crest factor), deeper and softer
        dict(f_start=85.0,  f_end=42.0, decay_time=0.190, punch_amount=0.45,
             click_len_ms=5.5, click_level=0.20, tilt_hf=0.9, drive=0.9),

        # Kick 5: mid-focused punch, a bit more click, slightly shorter tail
        dict(f_start=100.0, f_end=50.0, decay_time=0.160, punch_amount=0.65,
             click_len_ms=4.5, click_level=0.32, tilt_hf=1.3, drive=1.2),
    ]

    generated_paths = []

    # ------------------------------------------------
    # synthesis loop: generate 5 kicks
    # ------------------------------------------------
    for idx, kp in enumerate(kick_params, start=1):
        # Low-frequency body
        body = _make_body(
            f_start=kp["f_start"],
            f_end=kp["f_end"],
            decay_time=kp["decay_time"],
            punch_amount=kp["punch_amount"],
        )

        # Transient / click
        click = _make_click(
            click_len_ms=kp["click_len_ms"],
            click_level=kp["click_level"],
            tilt_hf=kp["tilt_hf"],
        )

        # Combine layers
        x = body + click

        # Gentle soft saturation for glue and transient shaping
        x = _soft_saturate(x, drive=kp["drive"])

        # Final cleanup, fades, and normalization
        x = _finalize(x)

        # Construct filename and path
        fname = f"kick_{idx:02d}.wav"
        fpath = os.path.join(path, fname)

        # Write 24-bit WAV for maximum quality (soundfile converts from float)
        sf.write(fpath, x, sr, subtype="PCM_24")

        generated_paths.append(fpath)

    return generated_paths


#!#!#!#!#! RUNNING STATEMENTS #!#!#!#!#!
#Example usage (set your desired absolute output folder path):
path = "/ABSOLUTE/OUTPUT/FOLDER"
generated_paths = _generate_kick(path)
print(generated_paths)
