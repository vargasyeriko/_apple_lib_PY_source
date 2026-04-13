#!/usr/bin/env python3
"""Minimal beat-locked DJ mixer. No sauce, no HPSS, no STFT tilt.
Just: BPM lock → trim to beat → phase-align start → short linear crossfade.
Outgoing drops fast (kills drums early), incoming rises on the grid.

    python djmix2.py
"""

from __future__ import annotations

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
STRETCH_LO, STRETCH_HI = 0.94, 1.06


def _fix_bpm(bpm: float) -> float:
    if bpm <= 0:
        return 126.0
    while bpm < 85:
        bpm *= 2.0
    while bpm > 175:
        bpm /= 2.0
    return float(bpm)


def _stereo(y: np.ndarray) -> np.ndarray:
    y = np.asarray(y, dtype=np.float32)
    if y.ndim == 1:
        return np.stack([y, y], axis=1)
    if y.shape[0] == 2 and y.shape[1] != 2:
        y = y.T
    if y.shape[1] == 1:
        y = np.repeat(y, 2, axis=1)
    return y


def _to_sound(y: np.ndarray) -> pygame.mixer.Sound:
    y = np.clip(_stereo(y), -1.0, 1.0)
    yi = (y * 32767.0).astype(np.int16)
    return pygame.sndarray.make_sound(np.ascontiguousarray(yi))


def _rms_norm(y: np.ndarray, target: float = 0.13) -> np.ndarray:
    rms = float(np.sqrt(np.mean(y * y) + 1e-12))
    if rms < 1e-6:
        return y
    return y * float(np.clip(target / rms, 0.5, 2.0))


def _load_and_lock(path: str, bpm_ref: float | None):
    """Load → fix BPM → stretch to ref → RMS norm → trim to first beat → Sound."""
    y, _ = librosa.load(path, sr=SR, mono=False)
    y = _stereo(y)
    mono = (y[:, 0] + y[:, 1]) * 0.5

    tempo, beat_frames = librosa.beat.beat_track(y=mono, sr=SR, hop_length=HOP)
    bpm = _fix_bpm(float(tempo.item() if hasattr(tempo, "item") else tempo))
    beats = librosa.frames_to_time(beat_frames, sr=SR, hop_length=HOP)

    # BPM lock: if close, match exactly; otherwise clamp stretch
    if bpm_ref is not None and bpm > 0:
        d = abs(bpm - bpm_ref)
        if d <= 6:
            tgt = bpm_ref
        else:
            tgt = bpm + np.clip(bpm_ref - bpm, -6, 6)
        rate = float(np.clip(tgt / bpm, STRETCH_LO, STRETCH_HI))
        if abs(rate - 1.0) > 5e-4:
            c0 = librosa.effects.time_stretch(y[:, 0], rate=rate)
            c1 = librosa.effects.time_stretch(y[:, 1], rate=rate)
            m = min(len(c0), len(c1))
            y = np.stack([c0[:m], c1[:m]], axis=1)
            beats = beats / rate
            bpm = tgt
    else:
        tgt = bpm

    y = _stereo(y).astype(np.float32)
    y = _rms_norm(y)

    # Trim so sample 0 = first beat
    if len(beats) > 0:
        cue = int(float(beats[0]) * SR)
        if 0 < cue < len(y) // 4:
            y = y[cue:]

    return _to_sound(y), float(tgt)


def _analyze(path: str) -> dict:
    y, _ = librosa.load(path, sr=SR, mono=True, duration=60.0)
    tempo, _ = librosa.beat.beat_track(y=y, sr=SR, hop_length=HOP)
    return {"bpm": _fix_bpm(float(tempo.item() if hasattr(tempo, "item") else tempo))}


def run(df: pd.DataFrame, fade_beats: float = 8.0):
    pygame.mixer.init(frequency=SR, size=-16, channels=2)
    pygame.mixer.set_num_channels(4)
    ch = [pygame.mixer.Channel(0), pygame.mixer.Channel(1)]

    paths = df["Path"].dropna().tolist()
    if not paths:
        print("❌ No paths")
        return

    print("\n🔍 scanning BPM…")
    meta = {p: _analyze(p) for p in tqdm(paths)}

    cur = {"bpm": None, "pri": 0, "t0": None}
    lock = threading.Lock()

    def mix(nxt: str):
        try:
            snd, bpm_new = _load_and_lock(nxt, cur["bpm"])
        except Exception as e:
            print(f"⚠️ {e}")
            return

        p, q = cur["pri"], 1 - cur["pri"]

        # First track
        if not ch[p].get_busy():
            ch[p].play(snd)
            ch[p].set_volume(1.0)
            cur["bpm"] = bpm_new
            cur["t0"] = time.perf_counter()
            print(f"\n▶ {os.path.basename(nxt)} | {bpm_new:.1f} BPM")
            return

        bpm = float(cur["bpm"] or bpm_new)
        bp = 60.0 / max(bpm, 1.0)

        # Wait for next beat on the outgoing deck
        if cur["t0"] is not None:
            elapsed = time.perf_counter() - cur["t0"]
            wait = bp - (elapsed % bp)
            if 0.01 < wait < bp * 0.95:
                time.sleep(wait)

        # Start incoming at vol 0 (trimmed to beat 1 = phase aligned)
        t0_new = time.perf_counter()
        ch[q].stop()
        ch[q].play(snd)
        ch[q].set_volume(0.0)

        # ── crossfade: linear, short, outgoing drops first ──
        fade_sec = fade_beats * bp
        fade_sec = float(np.clip(fade_sec, 2.0, 12.0))
        steps = max(60, int(fade_sec * 50))
        dt = fade_sec / steps

        for i in range(steps):
            t = i / (steps - 1)

            # Outgoing: drops faster (done at ~60% of the window)
            fo = max(0.0, 1.0 - t * 1.7)

            # Incoming: linear rise
            fi = t

            ch[p].set_volume(fo)
            ch[q].set_volume(fi)
            time.sleep(dt)

        ch[p].stop()
        ch[q].set_volume(1.0)
        cur["pri"] = q
        cur["bpm"] = bpm_new
        cur["t0"] = t0_new
        print(
            f"\n▶ {os.path.basename(nxt)} | {bpm_new:.1f} BPM | "
            f"fade {fade_sec:.1f}s ({fade_beats:.0f} beats)"
        )

    # Auto-advance: when the playing track ends, mix in the next one
    running = threading.Event()
    running.set()

    def _watchdog():
        while running.is_set():
            time.sleep(1.0)
            p = cur["pri"]
            if cur["bpm"] is not None and not ch[p].get_busy():
                with lock:
                    nxt = random.choice(paths)
                    print("\n⏭ auto-next (track ended)")
                    mix(nxt)

    wd = threading.Thread(target=_watchdog, daemon=True)
    wd.start()

    print(f"\n🎛 s=start | n=next | q=quit  ({fade_beats:.0f}-beat crossfade, auto-advances)")

    while True:
        cmd = input("👉 ").strip().lower()
        if cmd == "s":
            with lock:
                mix(random.choice(paths))
        elif cmd == "n":
            with lock:
                mix(random.choice(paths))
        elif cmd == "q":
            running.clear()
            for c in ch:
                if c.get_busy():
                    c.fadeout(600)
            print("🛑")
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
    print(len(df))
    print(df["Path"].apply(lambda x: os.path.exists(x)).all())

    df = df[
        (df["bpm_consistency"].round() == 100)
        & (df["dominant_bpm"] == 126)
        & (df["genre"].str.lower().str.contains("techno", na=False))
    ].copy()

    if df.empty:
        raise SystemExit("No rows after filter.")

    df = df.head(19)
    print(df[["bpm_consistency", "dominant_bpm", "genre"]].head())

    run(df, fade_beats=8.0)
