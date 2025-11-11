# ======================== IMPORTS ========================
import os
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
from IPython.display import Image, display

# -----######-----###### MAIN FUNCTION #####-----######-----

def _kick_0911_story_GET_dashboard_png(path_in, out_png_path=None, dpi=220):
    """
    Build a visual dashboard ("story") for a single kick sample, save it as PNG,
    display it inline in Jupyter, and print a ready-made prompt for a future chat
    to recreate a similar mono, clean, no-clipping kick in Python.
    """
    # ---------------- TQM HELPER ----------------
    def _tqm_bar(current_step, total_steps, msg=""):
        width = 30
        frac = current_step / float(total_steps)
        filled = int(width * frac)
        bar = "#" * filled + "-" * (width - filled)
        print(f"[TQM] |{bar}| {current_step}/{total_steps} {msg}")

    total_steps = 6
    step = 0

    # 1) Check input
    step += 1
    _tqm_bar(step, total_steps, "Checking file path...")
    if not os.path.isfile(path_in):
        raise FileNotFoundError(f"Input file not found: {path_in}")

    if out_png_path is None:
        base, _ = os.path.splitext(path_in)
        out_png_path = base + "_kick_story.png"

    # 2) Load audio
    step += 1
    _tqm_bar(step, total_steps, "Loading audio...")
    y, sr = librosa.load(path_in, sr=None, mono=True)
    if y.size == 0:
        raise ValueError("Audio file seems empty.")

    # 3) Core stats
    step += 1
    _tqm_bar(step, total_steps, "Computing core stats...")

    dur_sec = len(y) / sr
    eps = 1e-12
    peak = float(np.max(np.abs(y)))
    rms = float(np.sqrt(np.mean(y**2)) + eps)
    peak_dbfs = 20 * np.log10(peak + eps)
    rms_dbfs = 20 * np.log10(rms + eps)
    crest_factor = peak / (rms + eps)

    # Envelope
    win_env = max(1, int(0.001 * sr))  # ~1 ms smoothing
    kernel = np.ones(win_env) / win_env
    env = np.convolve(np.abs(y), kernel, mode="same")

    env_max = float(np.max(env) + eps)
    attack_thr = 0.1 * env_max
    decay_thr = 0.2 * env_max

    attack_idx = next((i for i, v in enumerate(env) if v >= attack_thr), None)
    decay_idx = None
    if attack_idx is not None:
        decay_idx = next(
            (i for i in range(attack_idx, len(env)) if env[i] <= decay_thr),
            None
        )

    attack_ms = attack_idx / sr * 1000 if attack_idx is not None else None
    decay_ms = decay_idx / sr * 1000 if decay_idx is not None else None

    # 4) Frequency analysis
    step += 1
    _tqm_bar(step, total_steps, "Analyzing spectrum...")
    fft = np.fft.rfft(y * np.hanning(len(y)))
    freqs = np.fft.rfftfreq(len(y), 1.0 / sr)
    mag_db = 20 * np.log10(np.abs(fft) + eps)

    fmin, fmax = 20, 200
    try:
        f0_series = librosa.yin(y, fmin=fmin, fmax=fmax, sr=sr)
        f0_clean = f0_series[np.isfinite(f0_series)]
        f0_hz = float(np.median(f0_clean)) if f0_clean.size > 0 else None
    except Exception:
        f0_hz = None

    # 5) Spectrogram
    step += 1
    _tqm_bar(step, total_steps, "Building spectrogram...")
    n_fft = 2048
    hop_length = max(1, int(0.0015 * sr))  # ~1.5 ms hop
    D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length, window="hann")
    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
    t = np.arange(len(y)) / sr

    # 6) Plot
    step += 1
    _tqm_bar(step, total_steps, "Rendering dashboard...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle(os.path.basename(path_in), fontsize=14, fontweight="bold")

    # Waveform
    ax_wave = axes[0, 0]
    ax_wave.plot(t, y, linewidth=1.0)
    ax_wave.axhline(0, color="gray", linewidth=0.5)
    ax_wave.set_title("Waveform")
    ax_wave.set_xlabel("Time (s)")
    ax_wave.set_ylabel("Amplitude")
    if attack_idx is not None:
        ax_wave.axvline(attack_idx / sr, color="red", linestyle="--", label="Attack")
    if decay_idx is not None:
        ax_wave.axvline(decay_idx / sr, color="orange", linestyle="--", label="Decay")
    ax_wave.legend(loc="upper right", fontsize=8)

    # Spectrum
    ax_spec = axes[0, 1]
    valid = (freqs >= 20) & (freqs <= 5000)
    ax_spec.plot(freqs[valid], mag_db[valid], linewidth=1.0)
    ax_spec.set_title("Magnitude Spectrum")
    ax_spec.set_xlabel("Frequency (Hz)")
    ax_spec.set_ylabel("Level (dB)")
    ax_spec.grid(alpha=0.2)
    if (f0_hz is not None) and (f0_hz >= 20):
        ax_spec.axvline(f0_hz, color="red", linestyle="--")
        ax_spec.text(
            f0_hz,
            np.max(mag_db[valid]),
            f"f0 ≈ {f0_hz:.1f} Hz",
            color="red",
            fontsize=8,
            va="bottom",
        )

    # Spectrogram
    ax_sgram = axes[1, 0]
    img = librosa.display.specshow(
        S_db,
        sr=sr,
        hop_length=hop_length,
        x_axis="time",
        y_axis="hz",
        ax=ax_sgram,
        cmap="magma",
    )
    ax_sgram.set_title("Spectrogram (dB)")
    fig.colorbar(img, ax=ax_sgram, format="%+2.0f dB")

    # Envelope + stats
    ax_env = axes[1, 1]
    ax_env.plot(t, env, linewidth=1.0)
    ax_env.set_title("Amplitude Envelope")
    ax_env.set_xlabel("Time (s)")
    ax_env.set_ylabel("Envelope")
    ax_env.grid(alpha=0.2)
    if attack_idx is not None:
        ax_env.axvline(attack_idx / sr, color="red", linestyle="--")
    if decay_idx is not None:
        ax_env.axvline(decay_idx / sr, color="orange", linestyle="--")

    stats_lines = [
        f"Duration: {dur_sec*1000:.1f} ms",
        f"Sample rate: {sr} Hz",
        f"Peak: {peak:.4f} ({peak_dbfs:.1f} dBFS)",
        f"RMS: {rms:.4f} ({rms_dbfs:.1f} dBFS)",
        f"Crest factor: {crest_factor:.2f}",
    ]
    if attack_ms is not None:
        stats_lines.append(f"Attack time: {attack_ms:.1f} ms")
    if decay_ms is not None:
        stats_lines.append(f"Decay point: {decay_ms:.1f} ms")
    if f0_hz is not None:
        stats_lines.append(f"Estimated f0: {f0_hz:.1f} Hz")

    stats_text = "\n".join(stats_lines)

    ax_env.text(
        0.02,
        0.98,
        stats_text,
        transform=ax_env.transAxes,
        fontsize=9,
        va="top",
        ha="left",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out_png_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)

    print(f"[SUCCESS] Kick dashboard saved -> {out_png_path}")
    display(Image(filename=out_png_path))

    # ---------- BUILD "NEXT CHAT" PROMPT TEXT ----------
    dur_ms = dur_sec * 1000.0
    safe_peak_dbfs = -1.0  # target peak for regenerated kick (no clipping)

    prompt_lines = [
        "CHATGPT – RECREATE THIS KICK SAMPLE IN PYTHON",
        "",
        "I’m sending you a dashboard image of a kick drum sample.",
        "From that image and these stats, please generate a new mono kick",
        "sample in Python with similar characteristics, at maximum quality,",
        "with no clipping.",
        "",
        "Target characteristics:",
        f"- Sample rate: {sr} Hz",
        f"- Approx duration: {dur_ms:.1f} ms",
        f"- Target peak level: {safe_peak_dbfs:.1f} dBFS (leave headroom, no clipping)",
        f"- Original peak: {peak_dbfs:.1f} dBFS, RMS: {rms_dbfs:.1f} dBFS",
        f"- Crest factor (original): {crest_factor:.2f}",
    ]

    if f0_hz is not None:
        prompt_lines.append(f"- Fundamental (f0) around: {f0_hz:.1f} Hz")

    if attack_ms is not None:
        prompt_lines.append(f"- Fast attack ~{attack_ms:.1f} ms")

    if decay_ms is not None:
        prompt_lines.append(f"- Main decay tail around {decay_ms:.1f} ms")

    prompt_lines += [
        "",
        "Constraints:",
        "- Output must be mono.",
        "- No limiting that causes clipping; leave a bit of headroom.",
        "- Render as a NumPy array (float32 or float64, range -1.0..1.0).",
        "- Then show Python code that could write it to WAV.",
        "",
        f'The dashboard image filename is: "{os.path.basename(out_png_path)}".',
        "Use both the image and the stats above to design the kick shape",
        "(envelope, pitch, transient/body, etc.).",
    ]

    prompt_text = "\n".join(prompt_lines)

    print("\n" + "=" * 72)
    print("COPY-PASTE THE TEXT BELOW INTO A NEW CHAT TO REBUILD THE SAMPLE:")
    print("=" * 72 + "\n")
    print(prompt_text)
    print("\n" + "=" * 72 + "\n")

    return out_png_path, prompt_text
