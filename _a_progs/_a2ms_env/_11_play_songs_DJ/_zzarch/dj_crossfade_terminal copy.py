#!/usr/bin/env python3
# Mix brain + sauce chain: fingerprints → scored recipe → dual-channel crossfade (no splice).
# Run: python dj_crossfade_terminal.py

# -----######-----######-----######-----######-----######
# _audio_FINAL_STABLE  +  THE_SAUCE
# -----######-----######-----######-----######-----######

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

# DJ pocket + safety
BPM_LO, BPM_HI = 118, 128
STRETCH_MIN, STRETCH_MAX = 0.94, 1.06


@dataclass
class MixRecipe:
    """How we treat THIS incoming vs the outgoing deck (the “best mix” plan)."""

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
    heat: float  # 0–100 compatibility vibe


def _ensure_stereo(y: np.ndarray) -> np.ndarray:
    y = np.asarray(y, dtype=np.float32)
    if y.ndim == 1:
        return np.stack([y, y], axis=1)
    if y.shape[0] == 2 and y.shape[1] != 2:
        y = y.T
    if y.shape[1] == 1:
        y = np.repeat(y, 2, axis=1)
    return y


def _soft_air(y: np.ndarray, sr: int, amount: float) -> np.ndarray:
    if amount <= 1e-6:
        return y
    y = _ensure_stereo(y)
    n = y.shape[0]
    out = np.zeros_like(y)
    d1 = int(0.031 * sr)
    d2 = int(0.048 * sr)
    d3 = int(0.071 * sr)
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
    """width 1.0 = mono-ish to  ~1.12 = wider."""
    y = _ensure_stereo(y)
    w = float(np.clip(width, 0.98, 1.14))
    L, R = y[:, 0], y[:, 1]
    M = (L + R) * 0.5
    S = (L - R) * 0.5
    L2 = M + w * S
    R2 = M - w * S
    mx = np.max(np.abs(np.stack([L2, R2], axis=1)), axis=1, keepdims=True) + 1e-8
    peak = np.maximum(mx, 1.0)
    out = np.stack([L2, R2], axis=1) / peak
    return np.clip(out, -1.0, 1.0)


def _harmonic_shimmer(y: np.ndarray, sr: int, amount: float) -> np.ndarray:
    """Gentle harmonic emphasis — HPSS is O(frames×bins); skip on long files."""
    if amount <= 1e-6:
        return y
    y = _ensure_stereo(y)
    # librosa hpss + scipy median_filter can hang minutes on full DJ-length tracks
    if y.shape[0] > int(sr * 75):
        return y
    out = np.zeros_like(y)
    amt = float(np.clip(amount, 0.0, 0.22))
    for c in range(2):
        h, p = librosa.effects.hpss(y[:, c].astype(np.float32))
        out[:, c] = (1.0 - amt) * y[:, c] + amt * (h * 1.06 + p * 0.98)
    return np.clip(out, -1.0, 1.0)


def _stft_tilt(y_stereo: np.ndarray, sr: int, highs_db: float, mud_db: float) -> np.ndarray:
    """Shelf-ish tilt in STFT domain (cheap ‘club’ curve)."""
    y = _ensure_stereo(y_stereo)
    n = y.shape[0]
    if n > int(sr * 240):
        # Full STFT→iSTFT on 5–8+ min tracks blocks the UI for tens of seconds
        return y
    freqs = librosa.fft_frequencies(sr=sr, n_fft=N_FFT)
    gh = 10.0 ** (float(highs_db) / 20.0)
    gm = 10.0 ** (float(mud_db) / 20.0)
    gain = np.ones((len(freqs), 1), dtype=np.float32)
    gain *= gm
    gain[freqs > 5500.0] *= gh
    gain[(freqs >= 180.0) & (freqs <= 420.0)] *= 0.92  # tiny mud pocket dip

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
    z = y * d
    return np.tanh(z)


def _master_sauce(y: np.ndarray, sr: int, recipe: MixRecipe) -> np.ndarray:
    """Heavy FX only where cheap; always finish with fast saturate / width / air."""
    y = _ensure_stereo(y).astype(np.float32)
    y = _harmonic_shimmer(y, sr, recipe.harmonic_shimmer)
    y = _stft_tilt(y, sr, recipe.shelf_high_db, recipe.mud_db)
    y = _soft_saturate(y, recipe.saturate)
    y = _ms_width(y, recipe.width)
    y = _soft_air(y, sr, recipe.wet)
    return np.clip(y, -1.0, 1.0)


def _fingerprint(path: str | os.PathLike) -> dict:
    """Fast spectral + energy signature (first ~75s)."""
    try:
        y, _ = librosa.load(path, sr=SR, mono=True, duration=75.0)
        if y.size < SR // 2:
            y = np.pad(y, (0, SR // 2 - len(y)))
        tempo, _ = librosa.beat.beat_track(y=y, sr=SR, hop_length=HOP)
        bpm = float(tempo.item() if hasattr(tempo, "item") else tempo)
        cent = float(np.median(librosa.feature.spectral_centroid(y=y, sr=SR)))
        # librosa expects roll_percent in (0, 1), not 0–100
        rol = float(np.median(librosa.feature.spectral_rolloff(y=y, sr=SR, roll_percent=0.85)))
        rms = float(np.sqrt(np.mean(np.square(y)) + 1e-12))
        h, p = librosa.effects.hpss(y.astype(np.float32))
        hp = float(np.sum(h * h) / (np.sum(h * h + p * p) + 1e-12))
        return {
            "bpm": bpm,
            "centroid": cent,
            "rolloff": rol,
            "rms": rms,
            "harmonic_ratio": hp,
        }
    except Exception:
        return {
            "bpm": 122.0,
            "centroid": 2000.0,
            "rolloff": 4000.0,
            "rms": 0.1,
            "harmonic_ratio": 0.5,
        }


def _bpm_plan(t_detect: float, bpm_ref: float | None) -> tuple[float, str]:
    t = float(t_detect) if t_detect and t_detect > 0 else 122.0
    t = float(np.clip(t, BPM_LO - 6, BPM_HI + 6))

    if bpm_ref is None:
        tgt = float(np.clip(t, BPM_LO, BPM_HI))
        return tgt, "start"

    ref = float(np.clip(bpm_ref, BPM_LO - 4, BPM_HI + 4))
    d = abs(t - ref)

    if d <= 3.5:
        return ref, "lock"
    if d <= 8.0:
        return float(np.clip(0.62 * ref + 0.38 * t, BPM_LO, BPM_HI)), "blend"
    if d <= 14.0:
        return float(np.clip(0.5 * (ref + t), BPM_LO, BPM_HI)), "nudge"
    step = np.sign(ref - t) * min(d * 0.4, 5.0)
    return float(np.clip(t + step, BPM_LO, BPM_HI)), "rescue"


def plan_mix(
    path_prev: str | None,
    path_next: str,
    bpm_deck: float | None,
    fp_map: dict[str, dict],
) -> MixRecipe:
    """
    Decide HOW to mix: spectral distance + BPM gap → recipe + heat score.
    Higher heat = friendlier blend (still artistic, not physics).
    """
    fn = fp_map[path_next]
    b_next = float(fn["bpm"])
    b_prev = float(bpm_deck) if bpm_deck else b_next
    b_prev = float(np.clip(b_prev, BPM_LO - 2, BPM_HI + 2))

    d_bpm = abs(b_next - b_prev)

    if path_prev is None or path_prev not in fp_map:
        heat = 100.0
        return MixRecipe(
            wet=0.07,
            width=1.045,
            harmonic_shimmer=0.06,
            shelf_high_db=1.2,
            mud_db=-0.8,
            saturate=1.02,
            bass_hold_exp=0.84,
            air_in_exp=1.05,
            fade_beats_mul=1.0,
            tag="OPEN",
            heat=heat,
        )

    fp = fp_map[path_prev]
    d_cent = abs(fn["centroid"] - fp["centroid"]) / (4000.0 + 1e-6)
    d_roll = abs(fn["rolloff"] - fp["rolloff"]) / (8000.0 + 1e-6)
    d_hp = abs(fn["harmonic_ratio"] - fp["harmonic_ratio"])

    # Heat: high = easier / tastier transition
    heat = 100.0
    heat -= min(38.0, d_bpm * 2.8)
    heat -= min(28.0, d_cent * 22.0)
    heat -= min(14.0, d_roll * 10.0)
    heat -= min(10.0, d_hp * 25.0)
    heat = float(np.clip(heat, 12.0, 100.0))

    # Base recipe from tier
    if d_bpm <= 3.5 and heat >= 72:
        tag = "TIGHT"
        wet, width = 0.06, 1.06
        hsh, sh, mud = 0.07, 1.8, -0.9
        sat, bh, ai = 1.03, 0.80, 1.08
        fmul = 0.85
    elif d_bpm <= 10 and heat >= 48:
        tag = "GLUE"
        wet, width = 0.11, 1.08
        hsh, sh, mud = 0.11, 2.4, -1.4
        sat, bh, ai = 1.06, 0.76, 1.12
        fmul = 1.0
    else:
        tag = "RESCUE"
        wet, width = 0.20, 1.10
        hsh, sh, mud = 0.14, 3.0, -2.0
        sat, bh, ai = 1.10, 0.72, 1.18
        fmul = 1.15

    # Spectral contrast: bright vs dark → tilt & width
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
        fade_beats_mul=float(np.clip(fmul, 0.75, 1.35)),
        tag=tag,
        heat=heat,
    )


def _prep_audio(path: str | os.PathLike, bpm_ref: float | None, recipe: MixRecipe):
    try:
        y, sr = librosa.load(path, sr=SR, mono=False)
    except Exception as e:
        raise RuntimeError(f"load failed: {path}: {e}") from e

    y = _ensure_stereo(y)
    mono = (y[:, 0] + y[:, 1]) * 0.5
    tempo, _ = librosa.beat.beat_track(y=mono, sr=sr, hop_length=HOP)
    t_in = float(tempo.item() if hasattr(tempo, "item") else tempo)

    tgt, btag = _bpm_plan(t_in, bpm_ref)
    rate = (tgt / t_in) if t_in > 1e-6 else 1.0
    rate = float(np.clip(rate, STRETCH_MIN, STRETCH_MAX))

    if abs(rate - 1.0) > 1e-4:
        c0 = librosa.effects.time_stretch(y[:, 0], rate=rate)
        c1 = librosa.effects.time_stretch(y[:, 1], rate=rate)
        m = min(len(c0), len(c1))
        y = np.stack([c0[:m], c1[:m]], axis=1)
    y = _ensure_stereo(y).astype(np.float32)

    y = _master_sauce(y, sr, recipe)

    y = np.clip(y, -1.0, 1.0)
    yi = (y * 32767.0).astype(np.int16)
    yi = np.ascontiguousarray(yi)
    sound = pygame.sndarray.make_sound(yi)
    return sound, tgt, btag


def _fade_curves(n: int, recipe: MixRecipe) -> tuple[np.ndarray, np.ndarray]:
    t = np.linspace(0.0, 1.0, n, endpoint=True)
    bh = recipe.bass_hold_exp
    ai = recipe.air_in_exp
    te = t**bh
    fo = np.cos(te * (np.pi / 2))
    ti = np.minimum(1.0, t**ai)
    fi = np.sin(ti * (np.pi / 2))
    e = np.sqrt(np.maximum(fo * fo + fi * fi, 1e-8))
    fo = fo / e
    fi = fi / e
    return fo.astype(np.float64), fi.astype(np.float64)


def _audio_FINAL_STABLE(df, fade_beats: float = 8.0):

    pygame.mixer.init(frequency=SR, size=-16, channels=2)
    pygame.mixer.set_num_channels(8)
    ch = [pygame.mixer.Channel(0), pygame.mixer.Channel(1)]

    paths = df["Path"].dropna().tolist()
    if not paths:
        print("❌ No paths")
        return

    print("\n🔍 fingerprinting tracks (BPM + spectrum + HPSS)…")
    fp_map = {p: _fingerprint(p) for p in tqdm(paths)}

    current: dict = {
        "bpm": None,
        "primary": 0,
        "path": None,
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

        if not ch[p].get_busy():
            ch[p].play(snd_new)
            ch[p].set_volume(1.0)
            current["bpm"] = bpm_new
            current["path"] = next_path
            print(
                f"\n▶️ {next_path}\n"
                f"   🎯 Mix brain: {recipe.tag} | heat {recipe.heat:.0f}/100 | "
                f"BPM≈{bpm_new:.1f} ({btag}) | sauce on"
            )
            return

        ch[q].stop()
        ch[q].play(snd_new)
        ch[q].set_volume(0.0)

        bpm = float(current["bpm"] or bpm_new)
        bpm = float(np.clip(bpm, BPM_LO, BPM_HI))
        beat_sec = 60.0 / max(bpm, 1e-6)
        eff_fade = float(np.clip(fade_beats * recipe.fade_beats_mul, 4.0, 36.0))
        fade_sec = eff_fade * beat_sec
        fade_sec = float(np.clip(fade_sec, 2.2, 36.0))

        steps = int(max(56, min(280, fade_sec * 72)))
        dt = fade_sec / steps

        fo, fi = _fade_curves(steps, recipe)

        for i in range(steps):
            ch[p].set_volume(float(fo[i]))
            ch[q].set_volume(float(fi[i]))
            time.sleep(dt)

        ch[p].fadeout(120)
        time.sleep(0.14)
        ch[p].stop()

        ch[q].set_volume(1.0)
        current["primary"] = q
        current["bpm"] = bpm_new
        current["path"] = next_path
        print(
            f"\n▶️ blended → {os.path.basename(next_path)}\n"
            f"   🎯 {recipe.tag} | heat {recipe.heat:.0f}/100 | "
            f"{fade_sec:.1f}s fade | W{recipe.width:.3f} shimmer{recipe.harmonic_shimmer:.2f} tilt+{recipe.shelf_high_db:.1f}dB"
        )

    print("\n🎛 s=start | n=next | q=quit  (mix brain + freq sauce active)")

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
        raise SystemExit(
            "No rows after filter (126 BPM, techno). Loosen filters or check genre strings in the pickle."
        )

    df = df.head(19)

    print(df[["bpm_consistency", "dominant_bpm", "genre"]].head())

    _audio_FINAL_STABLE(df, fade_beats=8.0)
