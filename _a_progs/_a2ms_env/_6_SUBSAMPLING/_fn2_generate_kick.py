# ===================== 0_FNS =====================
# -----######-----###### MAIN IMPORTS -----######-----######
import os, io, json, uuid, hmac, hashlib, socket, getpass
from datetime import datetime, timezone
import numpy as np
import soundfile as sf

# ----- helpers: shared -----
def _tqm_print(step, total, label):
    width = 28
    frac = step/float(total)
    filled = int(width*frac)
    bar = "█"*filled + " "*(width-filled)
    print(f"TQM | {label}: {int(frac*100):3d}%|{bar}| {step}/{total}")

def _normalize_peak(x, peak_db=-0.3):
    peak = float(np.max(np.abs(x)) + 1e-12)
    tgt = 10**(peak_db/20.0)
    return (x * (tgt/peak)).astype(np.float32)

def _safe_float(x):
    try:
        return float(x)
    except:
        return None

# ==========================================
#   KICK SYNTH HELPERS
# ==========================================
def _kick_body_with_pitch_and_harmonics(duration_s, sr, f_start, f_end, drive=2.0, harm_level=0.3):
    """
    Low-end body:
    - exponential downward pitch envelope
    - base sine + a couple harmonics
    - gentle tanh drive for weight
    """
    n_samples = max(1, int(duration_s * sr))
    t = np.arange(n_samples, dtype=np.float32) / sr
    duration = duration_s if duration_s > 0 else n_samples / float(sr)

    tau = t / duration
    freq = f_start * (f_end / f_start) ** tau
    phase = 2.0 * np.pi * np.cumsum(freq) / sr

    base = np.sin(phase)
    harm2 = np.sin(2.0 * phase)
    harm3 = np.sin(3.0 * phase)
    harm_stack = harm_level * (0.6 * harm2 + 0.4 * harm3)

    raw = base + harm_stack
    if drive > 0:
        raw = np.tanh(raw * drive) / np.tanh(drive)
    return raw.astype(np.float32)

def _kick_amp_envelope(duration_s, sr, shape_main=2.5, attack_ms=0.5, tail_ms=4.0):
    """
    Amplitude envelope:
    - micro fade-in
    - exponential-like decay
    - safety fade tail
    """
    n_samples = max(1, int(duration_s * sr))
    t = np.arange(n_samples, dtype=np.float32) / sr
    duration = duration_s if duration_s > 0 else n_samples / float(sr)

    tau = np.clip(t / duration, 0.0, 1.0)
    env = (1.0 - tau) ** shape_main

    attack_len = int(max(1, attack_ms * 1e-3 * sr))
    attack_len = min(attack_len, n_samples)
    env[:attack_len] *= np.linspace(0.0, 1.0, attack_len, dtype=np.float32)

    tail_len = int(max(1, tail_ms * 1e-3 * sr))
    tail_len = min(tail_len, n_samples)
    tail_env = np.linspace(1.0, 0.0, tail_len, dtype=np.float32)
    env[-tail_len:] *= tail_env

    return env.astype(np.float32)

def _kick_click_layer(sr, max_len_ms=8.0, seed=0, brightness_hz=3500.0):
    """
    Transient click:
    - high-passed noise + bright sine burst
    - very short with steep decay
    """
    rng = np.random.RandomState(seed)
    length = int(max(1, max_len_ms * 1e-3 * sr))
    t = np.arange(length, dtype=np.float32) / sr

    noise = rng.randn(length).astype(np.float32)
    hp_noise = np.zeros_like(noise)
    hp_noise[0] = noise[0]
    hp_noise[1:] = noise[1:] - noise[:-1]

    phase = 2.0 * np.pi * brightness_hz * t
    bright = np.sin(phase).astype(np.float32)

    click = 0.7 * hp_noise + 0.3 * bright
    tau = t / (t[-1] + 1e-9)
    decay = (1.0 - tau) ** 6.0
    click *= decay

    fade_len = max(1, int(2e-3 * sr))
    fade_len = min(fade_len, length)
    fade_tail = np.linspace(1.0, 0.0, fade_len, dtype=np.float32)
    click[-fade_len:] *= fade_tail

    return click.astype(np.float32)

def _kick_punch_layer(duration_s, sr, f_punch=160.0, len_ms=45.0):
    """
    Short mid-bass punch burst at start (120–200 Hz)
    """
    n_samples = max(1, int(duration_s * sr))
    full = np.zeros(n_samples, dtype=np.float32)

    burst_len = int(max(1, len_ms * 1e-3 * sr))
    burst_len = min(burst_len, n_samples)

    t = np.arange(burst_len, dtype=np.float32) / sr
    phase = 2.0 * np.pi * f_punch * t
    burst = np.sin(phase).astype(np.float32)

    tau = t / (t[-1] + 1e-9)
    decay = (1.0 - tau) ** 4.0
    burst *= decay

    full[:burst_len] += burst
    return full

def _kick_make_from_preset(p):
    """
    Build one kick from preset dict:
    - duration_s, f_start, f_end, drive, harm_level
    - click_gain, click_brightness_hz
    - punch_gain, punch_freq
    - env_shape, seed
    """
    sr = 44100
    duration_s = p["duration_s"]

    body = _kick_body_with_pitch_and_harmonics(
        duration_s=duration_s,
        sr=sr,
        f_start=p["f_start"],
        f_end=p["f_end"],
        drive=p["drive"],
        harm_level=p["harm_level"],
    )

    env = _kick_amp_envelope(
        duration_s=duration_s,
        sr=sr,
        shape_main=p["env_shape"],
        attack_ms=0.6,
        tail_ms=4.0,
    )
    body *= env

    n_samples = len(body)

    punch = _kick_punch_layer(
        duration_s=duration_s,
        sr=sr,
        f_punch=p["punch_freq"],
    ) * p["punch_gain"]

    click_short = _kick_click_layer(
        sr=sr,
        max_len_ms=7.0,
        seed=p["seed"],
        brightness_hz=p["click_brightness_hz"],
    ) * p["click_gain"]
    click = np.zeros(n_samples, dtype=np.float32)
    click[: len(click_short)] += click_short

    kick = body + punch + click

    fade_len = max(1, int(3e-3 * sr))
    fade_len = min(fade_len, n_samples)
    fade_tail = np.linspace(1.0, 0.0, fade_len, dtype=np.float32)
    kick[-fade_len:] *= fade_tail

    kick = _normalize_peak(kick, peak_db=-0.4)
    kick = np.clip(kick, -1.0, 1.0)
    return kick.astype(np.float32), sr

# Shared presets so provenance can see them too
_KICK_PRESETS = [
    dict(
        name="kick_01",
        duration_s=0.220,
        f_start=80.0,
        f_end=32.0,
        drive=2.2,
        harm_level=0.35,
        click_gain=0.55,
        click_brightness_hz=3700.0,
        punch_gain=0.40,
        punch_freq=160.0,
        env_shape=2.8,
        seed=101,
    ),
    dict(
        name="kick_02",
        duration_s=0.185,
        f_start=85.0,
        f_end=38.0,
        drive=2.0,
        harm_level=0.32,
        click_gain=0.50,
        click_brightness_hz=4000.0,
        punch_gain=0.45,
        punch_freq=180.0,
        env_shape=3.0,
        seed=102,
    ),
    dict(
        name="kick_03",
        duration_s=0.205,
        f_start=90.0,
        f_end=36.0,
        drive=2.4,
        harm_level=0.38,
        click_gain=0.60,
        click_brightness_hz=4200.0,
        punch_gain=0.42,
        punch_freq=170.0,
        env_shape=2.6,
        seed=103,
    ),
    dict(
        name="kick_04",
        duration_s=0.195,
        f_start=95.0,
        f_end=34.0,
        drive=2.6,
        harm_level=0.40,
        click_gain=0.70,
        click_brightness_hz=4500.0,
        punch_gain=0.48,
        punch_freq=190.0,
        env_shape=2.7,
        seed=104,
    ),
    dict(
        name="kick_05",
        duration_s=0.165,
        f_start=78.0,
        f_end=40.0,
        drive=2.1,
        harm_level=0.30,
        click_gain=0.52,
        click_brightness_hz=3800.0,
        punch_gain=0.50,
        punch_freq=200.0,
        env_shape=3.1,
        seed=105,
    ),
]

# -----######-----###### MAIN KICK FUNCTION -----######-----######
def _generate_kick(path=""):
    """
    Generate 5 high-quality kick drum one-shots.
    - Uses _KICK_PRESETS for consistent characters
    - Writes kick_01.wav ... kick_05.wav in 'path'
    - Returns list of absolute paths
    """
    if not path:
        path = os.getcwd()
    os.makedirs(path, exist_ok=True)

    total = len(_KICK_PRESETS)
    generated_paths = []

    for i, preset in enumerate(_KICK_PRESETS, start=1):
        _tqm_print(i, total, f"Synth {preset['name']}")

        kick, sr = _kick_make_from_preset(preset)
        fname = f"{preset['name']}.wav"
        fpath = os.path.join(path, fname)

        sf.write(fpath, kick, sr, subtype="PCM_24")
        generated_paths.append(os.path.abspath(fpath))

    return generated_paths

# =====================================
#   PROVENANCE / ATTESTATION + WM
# =====================================
def _bytes_sha256(data_bytes):
    return hashlib.sha256(data_bytes).hexdigest()

def _file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _make_hf_watermark(n, sr, seed_bytes, target_hz=None, dbfs=-45.0):
    """
    High-frequency watermark, extremely low level:
    HF sine + PN-phase + HF-tilt noise.
    """
    rng = np.random.default_rng(int.from_bytes(seed_bytes[:8], "big"))
    t = np.arange(n) / sr
    nyq = sr/2.0
    if target_hz is None:
        target_hz = min(17500.0, nyq*0.9) if sr >= 44100 else nyq*0.75

    carrier = np.sin(2*np.pi*target_hz*t)

    block = max(256, int(sr*0.004))
    flips = np.sign(rng.standard_normal(int(np.ceil(n/block))))
    phase_vec = np.repeat(flips, block)[:n]

    white = rng.standard_normal(n)
    hf_noise = white - np.concatenate(([0.0], white[:-1]))

    w = 0.7 * carrier * phase_vec + 0.3 * hf_noise
    w = w / (np.max(np.abs(w)) + 1e-12)
    amp = 10**(dbfs/20.0)
    return (w * amp).astype(np.float32)

# -----######-----###### ATTESTATION FUNCTION -----######-----######
def _attest_0110_proof_GET_manifest_prov(
    audio_path,
    generator_name="kick_1110_synthV2",
    params_dict=None,
    project_tag="YerikoTools",
    write_inplace=False,
    copy_suffix="_prov",
    add_watermark=True,
    wm_dbfs=-45.0,
    wm_hz=None,
    peak_after_wm_db=-0.3,
    sign_secret=None
):
    """
    Attest & (optionally) watermark an audio file.
    Writes sidecars (.json, .sha256, .txt) in the SAME directory.
    Returns a dict with paths + hashes.
    """
    steps = 7
    _tqm_print(1, steps, "Init Attest")

    if isinstance(sign_secret, str):
        sign_secret = sign_secret.encode("utf-8")
    params_dict = params_dict or {}

    folder, base = os.path.split(audio_path)
    stem, ext = os.path.splitext(base)
    if ext.lower() not in [".wav", ".flac", ".aiff", ".aif"]:
        raise ValueError("Provide a PCM WAV/AIFF/FLAC file path.")

    # 1) Read audio
    x, sr = sf.read(audio_path, always_2d=True)
    x = x.astype(np.float32)
    n, ch = x.shape[0], x.shape[1]
    _tqm_print(2, steps, "Read Audio")

    # 2) Hash BEFORE
    hash_before = _file_sha256(audio_path)
    _tqm_print(3, steps, "Hash Before")

    # 3) ID + signature seed
    now = datetime.now(timezone.utc).isoformat()
    att_id = str(uuid.uuid4())
    user = getpass.getuser()
    host = socket.gethostname()

    wm_seed_material = (att_id + json.dumps(params_dict, sort_keys=True)).encode("utf-8")
    sig_hex = None
    if sign_secret:
        sig_hex = hmac.new(sign_secret, wm_seed_material, hashlib.sha256).hexdigest()
        wm_seed_material += sig_hex.encode("utf-8")

    # 4) Watermark
    x_out = x.copy()
    if add_watermark:
        w = _make_hf_watermark(n, sr, hashlib.sha256(wm_seed_material).digest(), target_hz=wm_hz, dbfs=wm_dbfs)
        for c in range(ch):
            x_out[:, c] = x_out[:, c] + w
        _tqm_print(4, steps, "Watermark")
    else:
        _tqm_print(4, steps, "Watermark (skip)")

    # 5) Normalize
    x_out = _normalize_peak(x_out, peak_after_wm_db)
    _tqm_print(5, steps, "Normalize")

    # 6) Write audio
    out_audio_path = audio_path if write_inplace else os.path.join(folder, f"{stem}{copy_suffix}{ext}")
    sf.write(out_audio_path, x_out, sr, subtype="PCM_24")
    _tqm_print(6, steps, "Write Audio")

    # 7) Hash AFTER + manifests
    hash_after = _file_sha256(out_audio_path)
    manifest = {
        "attestation_version": "1.0",
        "attestation_id": att_id,
        "project_tag": project_tag,
        "generator_name": generator_name,
        "utc_timestamp_iso": now,
        "user": user,
        "host": host,
        "audio": {
            "path_in": os.path.abspath(audio_path),
            "path_out": os.path.abspath(out_audio_path),
            "sr": sr,
            "channels": ch,
            "duration_s": _safe_float(n/float(sr)),
            "hash_before_sha256": hash_before,
            "hash_after_sha256": hash_after,
            "peak_after_db": peak_after_wm_db
        },
        "params": params_dict,
        "watermark": {
            "enabled": bool(add_watermark),
            "level_dbfs": wm_dbfs,
            "target_hz": wm_hz,
            "scheme": "HF PN-phase + HF-tilt noise, uuid/hmac-seeded"
        },
        "signature": {
            "hmac_alg": "HMAC-SHA256" if sign_secret else None,
            "hmac_hex": sig_hex
        }
    }
    json_path = os.path.join(folder, f"{stem}.attestation.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    sha_path = os.path.join(folder, f"{stem}.sha256")
    with open(sha_path, "w", encoding="utf-8") as f:
        f.write(hash_after + "  " + os.path.basename(out_audio_path) + "\n")

    txt_path = os.path.join(folder, f"{stem}.attestation.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(
f"""PROVENANCE RECEIPT
Attestation ID : {att_id}
Project Tag    : {project_tag}
Generator      : {generator_name}
Timestamp UTC  : {now}
User@Host      : {user}@{host}

Input File     : {os.path.abspath(audio_path)}
Output File    : {os.path.abspath(out_audio_path)}
Sample Rate    : {sr} Hz
Channels       : {ch}
Duration (s)   : {n/float(sr):.6f}

SHA256 BEFORE  : {hash_before}
SHA256 AFTER   : {hash_after}

Watermark      : {"ENABLED" if add_watermark else "DISABLED"}
WM Level (dBFS): {wm_dbfs}
WM Target (Hz) : {wm_hz if wm_hz else "auto"}

Params JSON    : {json.dumps(params_dict, sort_keys=True)}

Signature Algo : {"HMAC-SHA256" if sign_secret else "None"}
HMAC (hex)     : {sig_hex if sig_hex else "None"}
"""
        )

    _tqm_print(7, steps, "Write Manifests")
    return {
        "audio_out": out_audio_path,
        "json": json_path,
        "sha256": sha_path,
        "txt": txt_path,
        "uuid": att_id,
        "hash_before": hash_before,
        "hash_after": hash_after
    }

# ==========================================
#   KICK CHAIN: GENERATE → ATTEST → INDEX
# ==========================================
def _prov_1110_kicks_GET_paths(
    output_dir,
    project_tag="YerikoTools",
    generator_name="kick_1110_synthV2",
    sign_secret=None,
    add_watermark=True,
    wm_dbfs=-45.0,
    wm_hz=None,
    peak_after_wm_db=-0.3,
    write_inplace=False,
    copy_suffix="_prov"
):
    """
    High-level chain:
      1) Generate 5 kicks into output_dir via _generate_kick.
      2) For each kick, write attestation sidecars (.json/.txt/.sha256) in SAME folder.
      3) Write an _index.txt summarizing everything.
    Returns:
      dict with {'output_dir','kicks','proofs','index'}
    """
    os.makedirs(output_dir, exist_ok=True)
    steps = 4
    _tqm_print(1, steps, "Generate Kicks")

    kick_paths = _generate_kick(output_dir)

    _tqm_print(2, steps, "Check Files")
    for p in kick_paths:
        if not os.path.exists(p):
            raise FileNotFoundError(f"Kick missing at path: {p}")
        if os.path.getsize(p) < 44:
            raise IOError(f"Kick too small to be valid WAV: {p}")

    _tqm_print(3, steps, "Attest All")
    proofs = []
    for idx, (p, preset) in enumerate(zip(kick_paths, _KICK_PRESETS), start=1):
        params = dict(
            kick_index=idx,
            kick_name=preset["name"],
            duration_s=preset["duration_s"],
            f_start=preset["f_start"],
            f_end=preset["f_end"],
            drive=preset["drive"],
            harm_level=preset["harm_level"],
            click_gain=preset["click_gain"],
            click_brightness_hz=preset["click_brightness_hz"],
            punch_gain=preset["punch_gain"],
            punch_freq=preset["punch_freq"],
            env_shape=preset["env_shape"],
            seed=preset["seed"],
        )
        proof = _attest_0110_proof_GET_manifest_prov(
            audio_path=p,
            generator_name=generator_name,
            params_dict=params,
            project_tag=project_tag,
            write_inplace=write_inplace,
            copy_suffix=copy_suffix,
            add_watermark=add_watermark,
            wm_dbfs=wm_dbfs,
            wm_hz=wm_hz,
            peak_after_wm_db=peak_after_wm_db,
            sign_secret=sign_secret
        )
        proofs.append(proof)

    _tqm_print(4, steps, "Index")
    idx_path = os.path.join(output_dir, "_index.txt")
    now = datetime.now(timezone.utc).isoformat()
    with open(idx_path, "w", encoding="utf-8") as f:
        f.write(f"KICK SESSION INDEX\nTimestamp UTC : {now}\nProject Tag   : {project_tag}\nGenerator     : {generator_name}\n\n")
        for idx, (p, proof) in enumerate(zip(kick_paths, proofs), start=1):
            f.write(
                f"[Kick {idx}]\n"
                f"  Audio Out : {os.path.basename(p)}\n"
                f"  Prov Audio: {os.path.basename(proof['audio_out'])}\n"
                f"  JSON      : {os.path.basename(proof['json'])}\n"
                f"  TXT       : {os.path.basename(proof['txt'])}\n"
                f"  SHA256    : {os.path.basename(proof['sha256'])}\n\n"
            )

    return {
        "output_dir": output_dir,
        "kicks": kick_paths,
        "proofs": proofs,
        "index": idx_path
    }

#!#!#!#!#! RUNNING STATEMENTS #!#!#!#!#!
#Example 1 – JUST generate the 5 kicks (no attest):
path = "/Users/yerik/Downloads/__DRUM_SAMPLE_TEST/_KICKS_OUT/_11_10_01-21___s14_d1-7140a_KICKS"
generated_paths = _generate_kick(path)
print(generated_paths)

# Example 2 – Generate + provenance + watermark, all in SAME folder:
# out_dir = "/Users/yerik/Downloads/__DRUM_SAMPLE_TEST/_KICKS_OUT/_11_10_01-21___s14_d1-7140a_KICKS"
# chain = _prov_1110_kicks_GET_paths(
#     output_dir=out_dir,
#     project_tag="YerikoTools",
#     generator_name="kick_1110_synthV2",
#     sign_secret=None,      # or b"your-secret"
#     add_watermark=True,
#     wm_dbfs=-45.0,
#     wm_hz=None,
#     peak_after_wm_db=-0.3,
#     write_inplace=False,
#     copy_suffix="_prov"
# )
# print(chain)

# # ===================== 0_FNS =====================
# import os
# import numpy as np
# import soundfile as sf

# def _sine_body_with_pitch_env(t, f_start, f_end):
#     """
#     Generate a low-frequency sine body with a smooth exponential downward pitch envelope.
#     f(t) goes from f_start to f_end over the duration of t.
#     """
#     # Exponential interpolation in frequency domain
#     # f(t) = f_start * (f_end/f_start)^(t/t_end)
#     if len(t) == 0:
#         return np.array([], dtype=np.float32)
#     duration = t[-1] - t[0] + (t[1] - t[0])  # approximate total duration
#     if duration <= 0:
#         duration = len(t) / 44100.0
#     # Normalized time
#     tau = t / duration
#     freq_env = f_start * (f_end / f_start) ** tau
#     # Integrate frequency to get phase: phase[n] = 2π * Σ_k freq[k]/sr
#     sr = 44100.0
#     phase = 2.0 * np.pi * np.cumsum(freq_env) / sr
#     body = np.sin(phase)
#     return body.astype(np.float32)

# def _amp_envelope(t, shape=2.5, fade_in_ms=0.5, fade_out_ms=2.0):
#     """
#     Exponential-style decay amplitude envelope with small fade-in and fade-out
#     to avoid clicks at start and end.
#     """
#     if len(t) == 0:
#         return np.array([], dtype=np.float32)
#     duration = t[-1] - t[0] + (t[1] - t[0])
#     if duration <= 0:
#         duration = len(t) / 44100.0
#     # Basic decay envelope
#     tau = np.clip(t / duration, 0.0, 1.0)
#     env = (1.0 - tau) ** shape

#     sr = 44100.0
#     # Fade-in
#     fade_in_len = int(max(1, fade_in_ms * 1e-3 * sr))
#     if fade_in_len > len(env):
#         fade_in_len = len(env)
#     env[:fade_in_len] *= np.linspace(0.0, 1.0, fade_in_len, dtype=np.float32)

#     # Fade-out
#     fade_out_len = int(max(1, fade_out_ms * 1e-3 * sr))
#     if fade_out_len > len(env):
#         fade_out_len = len(env)
#     env_tail = np.linspace(1.0, 0.0, fade_out_len, dtype=np.float32)
#     env[-fade_out_len:] *= env_tail

#     return env.astype(np.float32)

# def _click_layer(length, sr, seed=0, decay_ms=6.0, hp=True):
#     """
#     Short click / transient layer made from noise, optionally high-passed,
#     with a fast exponential-like decay.
#     """
#     rng = np.random.RandomState(seed)
#     n_samples = int(max(1, length))
#     noise = rng.randn(n_samples).astype(np.float32)

#     if hp:
#         # Simple first-order high-pass: y[n] = x[n] - x[n-1]
#         hp_noise = np.zeros_like(noise)
#         hp_noise[0] = noise[0]
#         hp_noise[1:] = noise[1:] - noise[:-1]
#         click = hp_noise
#     else:
#         click = noise

#     # Decay envelope
#     decay_len = n_samples
#     decay_time = np.linspace(0.0, 1.0, decay_len, dtype=np.float32)
#     # Steep decay around the very beginning
#     decay_env = (1.0 - decay_time) ** 4.0
#     click *= decay_env

#     # Additional micro fade-out to be extra-safe
#     fade_out_len = int(max(1, decay_ms * 1e-3 * sr))
#     fade_out_len = min(fade_out_len, n_samples)
#     fade_tail = np.linspace(1.0, 0.0, fade_out_len, dtype=np.float32)
#     click[-fade_out_len:] *= fade_tail

#     return click.astype(np.float32)

# def _punch_layer(t, f_mid, length_ms=40.0):
#     """
#     Optional mid-frequency punch layer (short sine burst around 150-300 Hz)
#     at the beginning of the kick to give more punch.
#     """
#     sr = 44100.0
#     total_len = len(t)
#     max_len = int(length_ms * 1e-3 * sr)
#     burst_len = min(total_len, max_len)
#     if burst_len <= 0:
#         return np.zeros_like(t, dtype=np.float32)

#     tb = np.arange(burst_len, dtype=np.float32) / sr
#     phase = 2.0 * np.pi * f_mid * tb
#     burst = np.sin(phase).astype(np.float32)

#     # fast decay for the burst
#     decay = (1.0 - (tb / (tb[-1] + 1e-9))) ** 3.0
#     burst *= decay.astype(np.float32)

#     layer = np.zeros_like(t, dtype=np.float32)
#     layer[:burst_len] += burst
#     return layer

# def _normalize_to_dbfs(signal, target_dbfs=-0.4):
#     """
#     Normalize the signal peak to target_dbfs (e.g., -0.4 dBFS),
#     avoiding division by zero and ensuring no clipping.
#     """
#     sig = np.asarray(signal, dtype=np.float32)
#     peak = np.max(np.abs(sig)) + 1e-12
#     target_linear = 10.0 ** (target_dbfs / 20.0)
#     sig = sig * (target_linear / peak)
#     return sig.astype(np.float32)

# def _generate_single_kick(duration_s, f_start, f_end, click_gain, punch_gain, seed):
#     """
#     Generate a single synthesized kick drum using:
#     - Low-frequency sine body with downward pitch envelope
#     - High-frequency transient click noise
#     - Optional mid-frequency punch burst
#     - Smooth amplitude envelope and normalization
#     """
#     sr = 44100.0
#     n_samples = int(duration_s * sr)
#     if n_samples < 1:
#         n_samples = 1
#     t = np.arange(n_samples, dtype=np.float32) / sr

#     # Low-frequency body
#     body = _sine_body_with_pitch_env(t, f_start=f_start, f_end=f_end)

#     # Amplitude envelope
#     env = _amp_envelope(t, shape=2.8, fade_in_ms=0.3, fade_out_ms=3.0)
#     body *= env

#     # Mid-frequency punch
#     punch = _punch_layer(t, f_mid=(f_start * 2.0), length_ms=40.0) * punch_gain

#     # Click/transient layer (5-7 ms)
#     click_len = int(0.005 * sr)
#     click = _click_layer(click_len, sr, seed=seed, decay_ms=6.0, hp=True) * click_gain
#     click_full = np.zeros_like(body, dtype=np.float32)
#     click_full[:len(click)] += click

#     # Sum layers
#     kick = body + punch + click_full

#     # Final gentle fade-out safety
#     fade_out_len = int(0.003 * sr)  # ~3 ms
#     fade_out_len = min(fade_out_len, len(kick))
#     fade_tail = np.linspace(1.0, 0.0, fade_out_len, dtype=np.float32)
#     kick[-fade_out_len:] *= fade_tail

#     # Normalize to around -0.4 dBFS peak
#     kick = _normalize_to_dbfs(kick, target_dbfs=-0.4)

#     # Extra safety: keep within -1..1
#     kick = np.clip(kick, -1.0, 1.0)
#     return kick.astype(np.float32)

# def _generate_kick(path=""):
#     """
#     Generate 5 high-quality synthesized kick drum one-shots inspired by the PDF stats:
#     - Durations ~160–230 ms
#     - Strong low-end body with downward pitch sweep
#     - Balanced sub / punch / click
#     - Clean transient and tail with no clicks
#     Saves:
#         kick_01.wav ... kick_05.wav
#     Returns:
#         List of 5 absolute file paths.
#     """
#     # Ensure output folder
#     if not path:
#         path = os.getcwd()
#     os.makedirs(path, exist_ok=True)

#     sr = 44100
#     # Durations taken from PDF (approx, in seconds)
#     durations = [
#         0.2295,  # kick_01
#         0.1943,  # kick_02
#         0.2288,  # kick_03
#         0.2299,  # kick_04
#         0.1615,  # kick_05
#     ]

#     # Fundamental pitch start/end (Hz) tuned roughly to typical suby techno/house kicks
#     f_start_list = [75.0, 80.0, 85.0, 90.0, 70.0]
#     f_end_list   = [35.0, 40.0, 45.0, 32.0, 45.0]

#     # Click and punch balances per kick
#     click_gains  = [0.50, 0.40, 0.55, 0.60, 0.35]
#     punch_gains  = [0.35, 0.30, 0.40, 0.45, 0.30]

#     seeds = [101, 102, 103, 104, 105]

#     generated_paths = []
#     for i in range(5):
#         duration_s = durations[i]
#         f_start = f_start_list[i]
#         f_end = f_end_list[i]
#         click_gain = click_gains[i]
#         punch_gain = punch_gains[i]
#         seed = seeds[i]

#         kick = _generate_single_kick(
#             duration_s=duration_s,
#             f_start=f_start,
#             f_end=f_end,
#             click_gain=click_gain,
#             punch_gain=punch_gain,
#             seed=seed,
#         )

#         file_name = f"kick_{i+1:02d}.wav"
#         out_path = os.path.join(path, file_name)

#         # Write as high-quality PCM_24 mono WAV at 44.1 kHz
#         sf.write(out_path, kick, sr, subtype="PCM_24")

#         generated_paths.append(os.path.abspath(out_path))

#     return generated_paths

# #!#!#!#!#! RUNNING STATEMENTS #!#!#!#!#!
# # Example usage (set your desired absolute output folder path):
# path = "/Users/yerik/Downloads/__DRUM_SAMPLE_TEST/_KICKS_OUT/_GENERATED_KICKS"
# generated_paths = _generate_kick(path)
# print(generated_paths)
