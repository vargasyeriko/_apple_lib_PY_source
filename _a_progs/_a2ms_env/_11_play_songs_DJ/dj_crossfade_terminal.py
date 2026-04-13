#!/usr/bin/env python3
"""Beat-phase-aligned DJ crossfade with mastering sauce.

Two pygame channels. Incoming trimmed to first beat, started ON the outgoing
beat grid, crossfaded over 16+ beats with equal-power curves + RMS matching.

Run:  python dj_crossfade_terminal.py
"""

from __future__ import annotations

import os
import random
import threading
import time
from dataclasses import dataclass

import librosa
import numpy as np
import pandas as pd
import pygame
from tqdm import tqdm

SR = 44100
HOP = 512
N_FFT = 2048

# Half/double BPM correction window
BPM_SANE_LO, BPM_SANE_HI = 85, 175

# Stretch pocket
STRETCH_MIN, STRETCH_MAX = 0.94, 1.06

# RMS loudness target
TARGET_RMS = 0.13


# ─────────────────────────── utilities ───────────────────────────


def _fix_bpm(bpm: float) -> float:
    """Snap librosa output into 85–175 (fixes half-time / double-time)."""
    if bpm <= 0:
        return 122.0
    while bpm < BPM_SANE_LO:
        bpm *= 2.0
    while bpm > BPM_SANE_HI:
        bpm /= 2.0
    return float(bpm)


def _ensure_stereo(y: np.ndarray) -> np.ndarray:
    y = np.asarray(y, dtype=np.float32)
    if y.ndim == 1:
        return np.stack([y, y], axis=1)
    if y.shape[0] == 2 and y.shape[1] != 2:
        y = y.T
    if y.shape[1] == 1:
        y = np.repeat(y, 2, axis=1)
    return y


def _rms_normalize(y: np.ndarray, target: float = TARGET_RMS) -> np.ndarray:
    rms = float(np.sqrt(np.mean(y * y) + 1e-12))
    if rms < 1e-6:
        return y
    gain = float(np.clip(target / rms, 0.5, 2.0))
    return y * gain


# ─────────────────────────── sauce chain ─────────────────────────


@dataclass
class MixRecipe:
    wet: float
    width: float
    harmonic_shimmer: float
    shelf_high_db: float
    mud_db: float
    saturate: float
    bass_hold_exp: float
    air_in_exp: float
    fade_beats_mul: float
    tag: str
    heat: float


def _soft_air(y: np.ndarray, sr: int, amount: float) -> np.ndarray:
    if amount <= 1e-6:
        return y
    y = _ensure_stereo(y)
    n = y.shape[0]
    out = np.zeros_like(y)
    d1, d2, d3 = int(0.031 * sr), int(0.048 * sr), int(0.071 * sr)
    g = float(np.clip(amount, 0.0, 0.38))
    for c in range(2):
        x = y[:, c].astype(np.float32)
        w = np.zeros_like(x)
        for d, a in ((d1, 0.45), (d2, 0.28), (d3, 0.15)):
            if 0 < d < n:
                w[d:] += a * x[:-d]
        out[:, c] = (1.0 - g) * x + g * w
    return np.clip(out, -1.0, 1.0)


def _ms_width(y: np.ndarray, width: float) -> np.ndarray:
    y = _ensure_stereo(y)
    w = float(np.clip(width, 0.98, 1.14))
    L, R = y[:, 0], y[:, 1]
    M, S = (L + R) * 0.5, (L - R) * 0.5
    L2, R2 = M + w * S, M - w * S
    mx = np.max(np.abs(np.stack([L2, R2], axis=1)), axis=1, keepdims=True) + 1e-8
    out = np.stack([L2, R2], axis=1) / np.maximum(mx, 1.0)
    return np.clip(out, -1.0, 1.0)


def _harmonic_shimmer(y: np.ndarray, sr: int, amount: float) -> np.ndarray:
    if amount <= 1e-6:
        return y
    y = _ensure_stereo(y)
    if y.shape[0] > int(sr * 75):
        return y
    out = np.zeros_like(y)
    amt = float(np.clip(amount, 0.0, 0.22))
    for c in range(2):
        h, p = librosa.effects.hpss(y[:, c].astype(np.float32))
        out[:, c] = (1.0 - amt) * y[:, c] + amt * (h * 1.06 + p * 0.98)
    return np.clip(out, -1.0, 1.0)


def _stft_tilt(y_stereo: np.ndarray, sr: int, highs_db: float, mud_db: float) -> np.ndarray:
    y = _ensure_stereo(y_stereo)
    n = y.shape[0]
    if n > int(sr * 240):
        return y
    freqs = librosa.fft_frequencies(sr=sr, n_fft=N_FFT)
    gh = 10.0 ** (float(highs_db) / 20.0)
    gm = 10.0 ** (float(mud_db) / 20.0)
    gain = np.ones((len(freqs), 1), dtype=np.float32)
    gain *= gm
    gain[freqs > 5500.0] *= gh
    gain[(freqs >= 180.0) & (freqs <= 420.0)] *= 0.92
    out = np.zeros_like(y)
    for c in range(2):
        d = y[:, c].astype(np.float32)
        S = librosa.stft(d, n_fft=N_FFT, hop_length=HOP)
        R = librosa.istft(S * gain, hop_length=HOP, n_fft=N_FFT, length=n)
        out[:, c] = R.astype(np.float32)
    return np.clip(out, -1.0, 1.0)


def _soft_saturate(y: np.ndarray, drive: float) -> np.ndarray:
    y = _ensure_stereo(y)
    d = float(np.clip(drive, 0.85, 1.18))
    return np.tanh(y * d)


def _master_sauce(y: np.ndarray, sr: int, recipe: MixRecipe) -> np.ndarray:
    y = _ensure_stereo(y).astype(np.float32)
    y = _harmonic_shimmer(y, sr, recipe.harmonic_shimmer)
    y = _stft_tilt(y, sr, recipe.shelf_high_db, recipe.mud_db)
    y = _soft_saturate(y, recipe.saturate)
    y = _ms_width(y, recipe.width)
    y = _soft_air(y, sr, recipe.wet)
    return np.clip(y, -1.0, 1.0)


# ─────────────────────── fingerprint + planning ──────────────────


def _fingerprint(path: str | os.PathLike) -> dict:
    try:
        y, _ = librosa.load(path, sr=SR, mono=True, duration=75.0)
        if y.size < SR // 2:
            y = np.pad(y, (0, SR // 2 - len(y)))
        tempo, _ = librosa.beat.beat_track(y=y, sr=SR, hop_length=HOP)
        bpm = _fix_bpm(float(tempo.item() if hasattr(tempo, "item") else tempo))
        cent = float(np.median(librosa.feature.spectral_centroid(y=y, sr=SR)))
        rol = float(np.median(librosa.feature.spectral_rolloff(y=y, sr=SR, roll_percent=0.85)))
        rms = float(np.sqrt(np.mean(np.square(y)) + 1e-12))
        h, p = librosa.effects.hpss(y.astype(np.float32))
        hp = float(np.sum(h * h) / (np.sum(h * h + p * p) + 1e-12))
        return {"bpm": bpm, "centroid": cent, "rolloff": rol, "rms": rms, "harmonic_ratio": hp}
    except Exception:
        return {"bpm": 122.0, "centroid": 2000.0, "rolloff": 4000.0, "rms": 0.1, "harmonic_ratio": 0.5}


def _bpm_plan(t_detect: float, bpm_ref: float | None) -> tuple[float, str]:
    t = _fix_bpm(t_detect)
    if bpm_ref is None:
        return t, "start"
    ref = float(bpm_ref)
    d = abs(t - ref)
    if d <= 3.5:
        return ref, "lock"
    if d <= 8.0:
        return float(np.clip(0.62 * ref + 0.38 * t, 85, 175)), "blend"
    if d <= 14.0:
        return float(np.clip(0.5 * (ref + t), 85, 175)), "nudge"
    step = np.sign(ref - t) * min(d * 0.4, 5.0)
    return float(np.clip(t + step, 85, 175)), "rescue"


def plan_mix(
    path_prev: str | None,
    path_next: str,
    bpm_deck: float | None,
    fp_map: dict[str, dict],
) -> MixRecipe:
    fn = fp_map.get(path_next) or _fingerprint(path_next)
    b_next = float(fn["bpm"])
    b_prev = float(bpm_deck) if bpm_deck else b_next

    d_bpm = abs(b_next - b_prev)

    if path_prev is None or path_prev not in fp_map:
        return MixRecipe(
            wet=0.07, width=1.045, harmonic_shimmer=0.06, shelf_high_db=1.2,
            mud_db=-0.8, saturate=1.02, bass_hold_exp=0.84, air_in_exp=1.05,
            fade_beats_mul=1.0, tag="OPEN", heat=100.0,
        )

    fp = fp_map[path_prev]
    d_cent = abs(fn["centroid"] - fp["centroid"]) / (4000.0 + 1e-6)
    d_roll = abs(fn["rolloff"] - fp["rolloff"]) / (8000.0 + 1e-6)
    d_hp = abs(fn["harmonic_ratio"] - fp["harmonic_ratio"])

    heat = 100.0 - min(38.0, d_bpm * 2.8) - min(28.0, d_cent * 22.0)
    heat -= min(14.0, d_roll * 10.0) + min(10.0, d_hp * 25.0)
    heat = float(np.clip(heat, 12.0, 100.0))

    if d_bpm <= 3.5 and heat >= 72:
        tag, wet, width = "TIGHT", 0.06, 1.06
        hsh, sh, mud = 0.07, 1.8, -0.9
        sat, bh, ai, fmul = 1.03, 0.82, 1.06, 1.0
    elif d_bpm <= 10 and heat >= 48:
        tag, wet, width = "GLUE", 0.11, 1.08
        hsh, sh, mud = 0.11, 2.4, -1.4
        sat, bh, ai, fmul = 1.06, 0.78, 1.10, 1.15
    else:
        tag, wet, width = "RESCUE", 0.20, 1.10
        hsh, sh, mud = 0.14, 3.0, -2.0
        sat, bh, ai, fmul = 1.10, 0.72, 1.18, 1.35

    if fn["centroid"] > fp["centroid"] + 900:
        sh += 0.7
        ai += 0.04
    elif fn["centroid"] + 900 < fp["centroid"]:
        mud -= 0.4
        bh -= 0.03
    if heat < 40:
        wet += 0.06
        hsh += 0.03
        width = min(1.13, width + 0.02)

    return MixRecipe(
        wet=float(np.clip(wet, 0.04, 0.28)),
        width=float(np.clip(width, 1.02, 1.14)),
        harmonic_shimmer=float(np.clip(hsh, 0.04, 0.18)),
        shelf_high_db=float(np.clip(sh, -1.0, 4.0)),
        mud_db=float(np.clip(mud, -3.0, 0.5)),
        saturate=float(np.clip(sat, 0.98, 1.14)),
        bass_hold_exp=float(np.clip(bh, 0.65, 0.92)),
        air_in_exp=float(np.clip(ai, 1.0, 1.28)),
        fade_beats_mul=float(np.clip(fmul, 0.75, 1.45)),
        tag=tag,
        heat=heat,
    )


# ───────────────────────── audio prep ────────────────────────────


def _prep_audio(path: str | os.PathLike, bpm_ref: float | None, recipe: MixRecipe):
    """Load → fix BPM → stretch → sauce → RMS → trim to first beat → Sound."""
    try:
        y, sr = librosa.load(path, sr=SR, mono=False)
    except Exception as e:
        raise RuntimeError(f"load failed: {path}: {e}") from e

    y = _ensure_stereo(y)
    mono = (y[:, 0] + y[:, 1]) * 0.5

    tempo, beat_frames = librosa.beat.beat_track(y=mono, sr=SR, hop_length=HOP)
    t_in = _fix_bpm(float(tempo.item() if hasattr(tempo, "item") else tempo))
    beat_times = librosa.frames_to_time(beat_frames, sr=SR, hop_length=HOP)

    tgt, btag = _bpm_plan(t_in, bpm_ref)
    rate = (tgt / t_in) if t_in > 1e-6 else 1.0
    rate = float(np.clip(rate, STRETCH_MIN, STRETCH_MAX))

    if abs(rate - 1.0) > 1e-4:
        c0 = librosa.effects.time_stretch(y[:, 0], rate=rate)
        c1 = librosa.effects.time_stretch(y[:, 1], rate=rate)
        m = min(len(c0), len(c1))
        y = np.stack([c0[:m], c1[:m]], axis=1)
        beat_times = beat_times / rate

    y = _ensure_stereo(y).astype(np.float32)
    y = _master_sauce(y, sr, recipe)
    y = _rms_normalize(y)

    # Trim to first detected beat so sample 0 IS a downbeat
    if len(beat_times) > 0:
        cue_sec = float(beat_times[0])
        cue_sample = int(cue_sec * SR)
        if 0 < cue_sample < len(y) // 4:
            y = y[cue_sample:]

    y = np.clip(y, -1.0, 1.0)
    yi = (y * 32767.0).astype(np.int16)
    yi = np.ascontiguousarray(yi)
    sound = pygame.sndarray.make_sound(yi)
    return sound, tgt, btag


# ───────────────────────── fade curves ───────────────────────────


def _fade_curves(n: int, recipe: MixRecipe) -> tuple[np.ndarray, np.ndarray]:
    """Equal-power crossfade with recipe-shaped hold/attack."""
    t = np.linspace(0.0, 1.0, n, endpoint=True)
    bh = recipe.bass_hold_exp   # <1 → outgoing holds longer before fading
    ai = recipe.air_in_exp      # >1 → incoming creeps in slowly then rises

    t_out = t ** bh
    t_in = np.clip(t ** ai, 0.0, 1.0)

    fo = np.cos(t_out * (np.pi / 2))
    fi = np.sin(t_in * (np.pi / 2))

    # Normalize so fo²+fi² ≈ 1 at every point → no volume dip
    e = np.sqrt(fo * fo + fi * fi + 1e-8)
    fo /= e
    fi /= e
    return fo.astype(np.float64), fi.astype(np.float64)


# ───────────────────────── player ────────────────────────────────


def _audio_FINAL_STABLE(df, fade_beats: float = 16.0):

    pygame.mixer.init(frequency=SR, size=-16, channels=2)
    pygame.mixer.set_num_channels(8)
    ch = [pygame.mixer.Channel(0), pygame.mixer.Channel(1)]

    paths = df["Path"].dropna().tolist()
    if not paths:
        print("❌ No paths")
        return

    print("\n🔍 fingerprinting tracks (BPM + spectrum)…")
    fp_map: dict[str, dict] = {p: _fingerprint(p) for p in tqdm(paths)}

    current: dict = {
        "bpm": None,
        "primary": 0,
        "path": None,
        "t0": None,           # perf_counter when the playing track started
    }
    lock = threading.Lock()

    def transition(next_path: str):

        recipe = plan_mix(current.get("path"), next_path, current.get("bpm"), fp_map)

        try:
            snd_new, bpm_new, btag = _prep_audio(next_path, current["bpm"], recipe)
        except Exception as e:
            print(f"⚠️ skip: {e}")
            return

        p = current["primary"]
        q = 1 - p

        # ── first track: just play ──
        if not ch[p].get_busy():
            ch[p].play(snd_new)
            ch[p].set_volume(1.0)
            current["bpm"] = bpm_new
            current["path"] = next_path
            current["t0"] = time.perf_counter()
            print(
                f"\n▶️ {os.path.basename(next_path)}\n"
                f"   🎯 {recipe.tag} | heat {recipe.heat:.0f}/100 | "
                f"BPM≈{bpm_new:.1f} ({btag})"
            )
            return

        # ── beat-phase alignment ──
        bpm = float(current["bpm"] or bpm_new)
        beat_period = 60.0 / max(bpm, 1.0)

        if current["t0"] is not None:
            elapsed = time.perf_counter() - current["t0"]
            phase = elapsed % beat_period
            wait = beat_period - phase
            # Only wait if we're meaningfully between beats
            if 0.015 < wait < beat_period * 0.97:
                time.sleep(wait)

        # ── start incoming at volume 0 (trimmed to first beat = phase aligned) ──
        t0_new = time.perf_counter()
        ch[q].stop()
        ch[q].play(snd_new)
        ch[q].set_volume(0.0)

        # ── crossfade ──
        eff_fade = float(np.clip(fade_beats * recipe.fade_beats_mul, 8.0, 48.0))
        fade_sec = eff_fade * beat_period
        fade_sec = float(np.clip(fade_sec, 3.5, 40.0))

        steps = max(100, int(fade_sec * 60))
        dt = fade_sec / steps

        fo, fi = _fade_curves(steps, recipe)

        for i in range(steps):
            ch[p].set_volume(float(fo[i]))
            ch[q].set_volume(float(fi[i]))
            time.sleep(dt)

        ch[p].fadeout(200)
        time.sleep(0.22)
        ch[p].stop()

        ch[q].set_volume(1.0)
        current["primary"] = q
        current["bpm"] = bpm_new
        current["path"] = next_path
        current["t0"] = t0_new

        print(
            f"\n▶️ blended → {os.path.basename(next_path)}\n"
            f"   🎯 {recipe.tag} | heat {recipe.heat:.0f}/100 | "
            f"BPM≈{bpm_new:.1f} ({btag}) | {fade_sec:.1f}s / {eff_fade:.0f} beats "
            f"| W{recipe.width:.2f} sat{recipe.saturate:.2f}"
        )

    print("\n🎛 s=start | n=next | q=quit  (beat-sync + sauce active)")

    while True:

        cmd = input("👉 ").strip().lower()

        if cmd == "s":
            with lock:
                transition(random.choice(paths))

        elif cmd == "n":
            with lock:
                transition(random.choice(paths))

        elif cmd == "q":
            for c in ch:
                if c.get_busy():
                    c.fadeout(800)
            print("🛑 STOP")
            break


if __name__ == "__main__":
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    pd.set_option("display.max_colwidth", None)

    path_name = os.environ.get(
        "DJ_TRACKS_PKL",
        "/Users/yerik/_apple_lib/_a_progs/_a2ms_env/_9_ML_project/data/processed/df_03_27_2026_aiff_tracks_data.pkl",
    )

    df = pd.read_pickle(path_name)
    df_raw = df.copy()

    print(len(df))
    print(df["Path"].apply(lambda x: os.path.exists(x)).all())

    df = df[
        (df["bpm_consistency"].round() == 100)
        & (df["dominant_bpm"] == 126)
        & (df["genre"].str.lower().str.contains("techno", na=False))
    ].copy()

    if df.empty:
        raise SystemExit("No rows after filter. Loosen filters or check genre strings.")

    df = df.head(19)

    print(df[["bpm_consistency", "dominant_bpm", "genre"]].head())

    _audio_FINAL_STABLE(df, fade_beats=16.0)
