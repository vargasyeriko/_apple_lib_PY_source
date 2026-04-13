#!/usr/bin/env python3
# Safe dual-channel crossfade: smart BPM (118–128), light “air” when BPMs fight,
# staggered faders (spectral-ish), no buffer splice → no rewind click.
# Run: python dj_crossfade_terminal.py

# -----######-----######-----######-----######-----######
# _audio_FINAL_STABLE
# -----######-----######-----######-----######-----######

import os
import random
import threading
import time

import librosa
import numpy as np
import pandas as pd
import pygame
from tqdm import tqdm

SR = 44100
HOP = 512

# DJ pocket + safety
BPM_LO, BPM_HI = 118, 128
STRETCH_MIN, STRETCH_MAX = 0.94, 1.06


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
    """Tiny multi-tap delay — masks rough BPM joins; amount ~0.04–0.22."""
    if amount <= 1e-6:
        return y
    y = _ensure_stereo(y)
    n = y.shape[0]
    out = np.zeros_like(y)
    d1 = int(0.031 * sr)
    d2 = int(0.048 * sr)
    d3 = int(0.071 * sr)
    g = float(np.clip(amount, 0.0, 0.35))
    for c in range(2):
        x = y[:, c].astype(np.float32)
        w = np.zeros_like(x)
        for d, a in ((d1, 0.45), (d2, 0.28), (d3, 0.15)):
            if 0 < d < n:
                w[d:] += a * x[:-d]
        out[:, c] = (1.0 - g) * x + g * w
    return np.clip(out, -1.0, 1.0)


def _bpm_plan(t_detect: float, bpm_ref: float | None) -> tuple[float, float, str]:
    """
    Pick stretch target BPM + wet hint.
    Close BPMs lock; mid gap blends toward pocket; big gap caps stretch + more air.
    """
    t = float(t_detect) if t_detect and t_detect > 0 else 122.0
    t = float(np.clip(t, BPM_LO - 6, BPM_HI + 6))

    if bpm_ref is None:
        tgt = float(np.clip(t, BPM_LO, BPM_HI))
        return tgt, 0.06, "start"

    ref = float(np.clip(bpm_ref, BPM_LO - 4, BPM_HI + 4))
    d = abs(t - ref)

    if d <= 3.5:
        tgt = ref
        wet = 0.05
        tag = "lock"
    elif d <= 8.0:
        tgt = float(np.clip(0.62 * ref + 0.38 * t, BPM_LO, BPM_HI))
        wet = 0.08
        tag = "blend"
    elif d <= 14.0:
        tgt = float(np.clip(0.5 * (ref + t), BPM_LO, BPM_HI))
        wet = 0.12
        tag = "nudge"
    else:
        # Hard mismatch: only partial lock + more glue
        step = np.sign(ref - t) * min(d * 0.4, 5.0)
        tgt = float(np.clip(t + step, BPM_LO, BPM_HI))
        wet = 0.19
        tag = "rescue"

    return tgt, wet, tag


def _prep_audio(path: str | os.PathLike, bpm_ref: float | None):
    """Stereo pygame Sound, effective BPM after stretch, debug tag."""
    try:
        y, sr = librosa.load(path, sr=SR, mono=False)
    except Exception as e:
        raise RuntimeError(f"load failed: {path}: {e}") from e

    y = _ensure_stereo(y)
    mono = (y[:, 0] + y[:, 1]) * 0.5
    tempo, _ = librosa.beat.beat_track(y=mono, sr=sr, hop_length=HOP)
    t_in = float(tempo.item() if hasattr(tempo, "item") else tempo)

    tgt, wet, tag = _bpm_plan(t_in, bpm_ref)
    rate = (tgt / t_in) if t_in > 1e-6 else 1.0
    rate = float(np.clip(rate, STRETCH_MIN, STRETCH_MAX))

    if abs(rate - 1.0) > 1e-4:
        c0 = librosa.effects.time_stretch(y[:, 0], rate=rate)
        c1 = librosa.effects.time_stretch(y[:, 1], rate=rate)
        m = min(len(c0), len(c1))
        y = np.stack([c0[:m], c1[:m]], axis=1)
    y = _ensure_stereo(y).astype(np.float32)

    y = _soft_air(y, sr, wet)

    y = np.clip(y, -1.0, 1.0)
    yi = (y * 32767.0).astype(np.int16)
    yi = np.ascontiguousarray(yi)
    sound = pygame.sndarray.make_sound(yi)
    return sound, tgt, tag


def _analyze_track(path: str | os.PathLike):
    y, _ = librosa.load(path, sr=SR, mono=True)
    tempo, _ = librosa.beat.beat_track(y=y, sr=SR, hop_length=HOP)
    tempo = float(tempo.item() if hasattr(tempo, "item") else tempo)
    return {"bpm": tempo}


def _fade_curves(t: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Staggered “band faders”: lows stay a hair longer on outgoing, highs come in
    a bit faster on incoming — safe, no STFT splice.
    """
    t = np.clip(t, 0.0, 1.0)
    # outgoing: slightly slower decay (bass holds)
    te = t ** 0.82
    fo = np.cos(te * (np.pi / 2))
    # incoming: slightly eager
    ti = np.minimum(1.0, t ** 1.07)
    fi = np.sin(ti * (np.pi / 2))
    # gentle re-normalize so we don't dip too quiet in the middle
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

    print("\n🔍 analyzing BPM...")
    meta = {p: _analyze_track(p) for p in tqdm(paths)}

    current = {
        "bpm": None,
        "primary": 0,
    }
    lock = threading.Lock()

    def transition(next_path: str):

        try:
            snd_new, bpm_new, tag = _prep_audio(next_path, current["bpm"])
        except Exception as e:
            print(f"⚠️ skip: {e}")
            return

        p = current["primary"]
        q = 1 - p

        if not ch[p].get_busy():
            ch[p].play(snd_new)
            ch[p].set_volume(1.0)
            current["bpm"] = bpm_new
            print(f"\n▶️ {next_path} | BPM≈{bpm_new:.1f} ({tag})")
            return

        # Incoming on secondary; never stop primary until fade ends (no splice jump)
        ch[q].stop()
        ch[q].play(snd_new)
        ch[q].set_volume(0.0)

        bpm = float(current["bpm"] or bpm_new)
        bpm = float(np.clip(bpm, BPM_LO, BPM_HI))
        beat_sec = 60.0 / max(bpm, 1e-6)
        fade_sec = float(np.clip(fade_beats, 4.0, 32.0)) * beat_sec
        fade_sec = float(np.clip(fade_sec, 2.0, 32.0))

        steps = int(max(48, min(240, fade_sec * 60)))
        dt = fade_sec / steps

        tlin = np.linspace(0.0, 1.0, steps, endpoint=True)
        fo, fi = _fade_curves(tlin)

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
        print(f"\n▶️ {next_path} | BPM≈{bpm_new:.1f} ({tag}) | fade {fade_sec:.1f}s")

    print("\n🎛 s=start | n=next | q=quit")

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

    df_raw = pd.read_pickle(path_name)

    print(len(df))

    print(df["Path"].apply(lambda x: os.path.exists(x)).all())

    df = df[
        (df["bpm_consistency"].round() == 100)
        & (df["dominant_bpm"] == 126)
        & (df["genre"].str.lower().str.contains("deep house"))
        & (df["key_dj"].str.contains("1A"))
    ].copy()


    print(df[["bpm_consistency", "dominant_bpm", "genre"]].head())

    _audio_FINAL_STABLE(df, fade_beats=8.0)
