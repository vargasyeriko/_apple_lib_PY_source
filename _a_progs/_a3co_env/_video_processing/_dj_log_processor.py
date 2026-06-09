#!/Users/yerik/_apple_lib/_b_envs/3co_env/bin/python3
"""
DJ-LOG Video Processor v2 — Per-Video Pipeline

Processes each MP4 INDIVIDUALLY (sync audio, compress, export),
then fast-concats at the end. Resumable — skips already-done videos.

Usage:
    python _dj_log_processor.py
"""

import subprocess, json, os, sys, tempfile, time, re
from pathlib import Path
import numpy as np
from scipy.signal import fftconvolve, butter, sosfiltfilt

# ═════════════════════════════════════════════════════════════════════════════
INPUT_DIR  = Path(__file__).resolve().parent / "_1_DJ-LOG_NOT_passed"
OUTPUT_DIR = INPUT_DIR / "output_vids"
FFMPEG     = "ffmpeg"
FFPROBE    = "ffprobe"

FULL_W, FULL_H   = 1920, 1080
FULL_VIDEO_BR     = "2000k"
FULL_MAXRATE      = "3500k"
FULL_BUFSIZE      = "5000k"
AUDIO_BR          = "256k"
AUDIO_SR          = 48000

IG_W, IG_H        = 1080, 1350
CLIP_DUR          = 60
N_CLIPS           = 10
CLIP_VIDEO_BR     = "3500k"

SYNC_SR           = 8000
SYNC_DUR          = 40
BP_LO, BP_HI     = 80, 3500

ENERGY_WIN        = 1
SMOOTH_WIN        = 20
MIN_GAP           = 90
EDGE_MARGIN       = 120


def _log(msg, char="═"):
    print(f"\n{char * 72}\n  {msg}\n{char * 72}", flush=True)

def _step(msg):
    print(f"  → {msg}", flush=True)

def _run(cmd, desc=None, capture=True, check=True):
    if desc:
        _step(desc)
    kw = dict(capture_output=True, text=True) if capture else {}
    r = subprocess.run(cmd, **kw)
    if check and r.returncode != 0:
        err = (r.stderr or "")[:600] if capture else ""
        raise RuntimeError(f"Command failed: {' '.join(str(c) for c in cmd[:8])}...\n{err}")
    return r

def _duration(path):
    r = _run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
              "-of", "default=nw=1:nk=1", str(path)])
    return float(r.stdout.strip())

def _audio_np(path, sr=SYNC_SR, offset=0, duration=None):
    tmp = tempfile.mktemp(suffix=".raw")
    cmd = [FFMPEG, "-y", "-v", "error"]
    if offset > 0:
        cmd += ["-ss", str(offset)]
    if duration is not None:
        cmd += ["-t", str(duration)]
    cmd += ["-i", str(path), "-vn", "-ac", "1", "-ar", str(sr),
            "-f", "s16le", "-acodec", "pcm_s16le", tmp]
    _run(cmd)
    data = np.fromfile(tmp, dtype=np.int16).astype(np.float32)
    os.unlink(tmp)
    return data

def _bandpass(data, sr, lo=BP_LO, hi=BP_HI):
    nyq = sr / 2.0
    sos = butter(4, [max(lo/nyq, 0.001), min(hi/nyq, 0.999)], btype="band", output="sos")
    return sosfiltfilt(sos, data).astype(np.float32)

def _xcorr_offset(ref, target, sr):
    r = ref - np.mean(ref)
    t = target - np.mean(target)
    r_norm = np.linalg.norm(r)
    if r_norm < 1e-10:
        return 0.0, 0.0
    r = r / r_norm
    corr = fftconvolve(t, r[::-1], mode="valid")
    peak_idx = int(np.argmax(np.abs(corr)))
    peak_val = float(np.abs(corr[peak_idx]))
    seg = t[peak_idx : peak_idx + len(r)]
    seg_norm = np.linalg.norm(seg)
    confidence = peak_val / (seg_norm + 1e-10)
    return peak_idx / sr, confidence


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 1 — DISCOVER
# ═════════════════════════════════════════════════════════════════════════════
def phase1_discover():
    _log("PHASE 1 · Discovering files")
    mp4s = sorted([f for f in INPUT_DIR.iterdir()
                   if f.suffix.upper() == ".MP4" and not f.name.startswith(".")],
                  key=lambda p: p.name)
    wavs = sorted([f for f in INPUT_DIR.iterdir()
                   if f.suffix.upper() == ".WAV" and not f.name.startswith(".")],
                  key=lambda p: p.name)

    mp4_info = []
    for f in mp4s:
        dur = _duration(f)
        print(f"      {f.name:30s}  {dur/60:6.1f} min  {f.stat().st_size/(1024**3):.1f} GB")
        mp4_info.append({"path": f, "duration": dur})

    wav_info = []
    for f in wavs:
        dur = _duration(f)
        print(f"      {f.name:30s}  {dur/60:6.1f} min")
        wav_info.append({"path": f, "duration": dur})

    return mp4_info, wav_info


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 2 — SYNC
# ═════════════════════════════════════════════════════════════════════════════
def phase2_sync(mp4_info, wav_info):
    _log("PHASE 2 · Audio sync via cross-correlation")

    wav_cache = {}
    for w in wav_info:
        wp = w["path"]
        _step(f"Loading {wp.name} at {SYNC_SR} Hz …")
        raw = _audio_np(wp, sr=SYNC_SR)
        raw = _bandpass(raw, SYNC_SR)
        wav_cache[wp] = raw
        print(f"      {len(raw)} samples  ({len(raw)/SYNC_SR:.1f} s)")

    cum_t = 0.0
    sync_map = []

    for mi in mp4_info:
        mp4 = mi["path"]
        dur = mi["duration"]
        _step(f"Correlating {mp4.name}  (video_t = {cum_t:.1f} s) …")
        ref = _audio_np(mp4, sr=SYNC_SR, duration=SYNC_DUR)
        ref = _bandpass(ref, SYNC_SR)

        best_wav, best_off, best_conf = None, 0.0, -1.0
        for wp, wav_arr in wav_cache.items():
            off, conf = _xcorr_offset(ref, wav_arr, SYNC_SR)
            print(f"      vs {wp.name:30s}  offset={off:9.2f} s  conf={conf:.4f}")
            if conf > best_conf:
                best_wav, best_off, best_conf = wp, off, conf

        print(f"      Best → {best_wav.name}  offset={best_off:.2f} s  conf={best_conf:.4f}")

        sync_map.append({
            "mp4": mp4, "mp4_dur": dur, "video_t": cum_t,
            "wav": best_wav, "wav_off": best_off, "confidence": best_conf,
        })
        cum_t += dur

    # consistency check
    _step("Consistency check …")
    for i in range(1, len(sync_map)):
        prev, curr = sync_map[i-1], sync_map[i]
        if prev["wav"] == curr["wav"]:
            expected = prev["wav_off"] + prev["mp4_dur"]
            drift = abs(curr["wav_off"] - expected)
            status = "OK" if drift < 2.0 else f"GAP {drift:.1f}s"
            print(f"      [{i-1}→{i}]  expected={expected:.1f}  actual={curr['wav_off']:.1f}  {status}")
        else:
            print(f"      [{i-1}→{i}]  WAV switch: {prev['wav'].name} → {curr['wav'].name}")

    return sync_map, cum_t


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 3 — ENCODE EACH VIDEO INDIVIDUALLY
# ═════════════════════════════════════════════════════════════════════════════
def _find_next_wav_for_tail(sync_map, idx, remaining):
    if idx + 1 >= len(sync_map):
        return None
    nxt = sync_map[idx + 1]
    if nxt["confidence"] < 0.05 or nxt["wav"] is None:
        return None
    nxt_wav, nxt_off = nxt["wav"], nxt["wav_off"]
    tail_start = max(0.0, nxt_off - remaining)
    tail_dur = min(remaining, nxt_off - tail_start)
    return (nxt_wav, tail_start, tail_dur) if tail_dur >= 1.0 else None


def phase3_encode_per_video(sync_map):
    _log("PHASE 3 · Encoding each video individually (resumable)")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    compressed = []
    for i, entry in enumerate(sync_map):
        mp4       = entry["mp4"]
        mp4_dur   = entry["mp4_dur"]
        wav_path  = entry["wav"]
        wav_off   = entry["wav_off"]
        wav_dur   = _duration(wav_path)
        use_wav   = entry["confidence"] >= 0.05

        out_vid = OUTPUT_DIR / f"part_{i+1:02d}.mp4"
        compressed.append(out_vid)

        # --- SKIP if already done ---
        if out_vid.exists():
            existing_dur = _duration(out_vid)
            if abs(existing_dur - mp4_dur) < 2.0:
                _step(f"[{i+1}/{len(sync_map)}] {mp4.name} → ALREADY DONE ({existing_dur/60:.1f} min), skipping")
                continue

        _step(f"[{i+1}/{len(sync_map)}] {mp4.name} ({mp4_dur/60:.1f} min)")

        # --- Build audio segment ---
        seg_audio = OUTPUT_DIR / f"_tmp_audio_{i}.wav"

        if use_wav and wav_off + mp4_dur <= wav_dur + 0.5:
            _step(f"  Audio: {wav_path.name} [{wav_off:.1f}→{wav_off+mp4_dur:.1f}]")
            _run([FFMPEG, "-y", "-v", "error",
                  "-ss", str(wav_off), "-t", str(mp4_dur),
                  "-i", str(wav_path),
                  "-ac", "1", "-ar", str(AUDIO_SR), "-acodec", "pcm_s16le",
                  str(seg_audio)])
        elif use_wav and wav_off < wav_dur:
            avail = wav_dur - wav_off
            remaining = mp4_dur - avail
            tail = _find_next_wav_for_tail(sync_map, i, remaining)
            part_a = OUTPUT_DIR / f"_tmp_pA_{i}.wav"
            part_b = OUTPUT_DIR / f"_tmp_pB_{i}.wav"
            _run([FFMPEG, "-y", "-v", "error",
                  "-ss", str(wav_off), "-t", str(avail),
                  "-i", str(wav_path),
                  "-ac", "1", "-ar", str(AUDIO_SR), "-acodec", "pcm_s16le",
                  str(part_a)])
            if tail:
                tw, ts, td = tail
                _step(f"  Audio: cross-WAV → {tw.name} [0→{ts+td:.1f}]")
                _run([FFMPEG, "-y", "-v", "error",
                      "-ss", str(ts), "-t", str(td), "-i", str(tw),
                      "-ac", "1", "-ar", str(AUDIO_SR), "-acodec", "pcm_s16le",
                      str(part_b)])
            else:
                _step(f"  Audio: MP4 fallback for last {remaining:.1f}s")
                _run([FFMPEG, "-y", "-v", "error",
                      "-ss", str(avail), "-t", str(remaining),
                      "-i", str(entry["mp4"]),
                      "-vn", "-ac", "1", "-ar", str(AUDIO_SR), "-acodec", "pcm_s16le",
                      str(part_b)])
            clist = OUTPUT_DIR / f"_tmp_cl_{i}.txt"
            clist.write_text(f"file '{part_a}'\nfile '{part_b}'\n")
            _run([FFMPEG, "-y", "-v", "error",
                  "-f", "concat", "-safe", "0", "-i", str(clist),
                  "-c", "copy", str(seg_audio)])
            for f in (part_a, part_b, clist):
                f.unlink(missing_ok=True)
        else:
            _step(f"  Audio: MP4 internal (low confidence)")
            _run([FFMPEG, "-y", "-v", "error",
                  "-i", str(entry["mp4"]),
                  "-vn", "-ac", "1", "-ar", str(AUDIO_SR), "-acodec", "pcm_s16le",
                  str(seg_audio)])

        # --- Encode this video ---
        _step(f"  Encoding 5.3K → 1080p …")
        t0 = time.time()
        _run([
            FFMPEG, "-y",
            "-i", str(mp4),
            "-i", str(seg_audio),
            "-map", "0:v:0", "-map", "1:a:0",
            "-vf", f"scale={FULL_W}:{FULL_H}:flags=lanczos,format=yuv420p",
            "-c:v", "h264_videotoolbox",
            "-b:v", FULL_VIDEO_BR,
            "-maxrate", FULL_MAXRATE, "-bufsize", FULL_BUFSIZE,
            "-profile:v", "high",
            "-c:a", "aac", "-b:a", AUDIO_BR, "-ac", "2", "-ar", str(AUDIO_SR),
            "-movflags", "+faststart",
            str(out_vid),
        ], capture=False)
        elapsed = time.time() - t0

        seg_audio.unlink(missing_ok=True)

        sz = out_vid.stat().st_size / (1024**3)
        _step(f"  DONE: {out_vid.name}  {sz:.2f} GB  ({elapsed/60:.1f} min)")

    return compressed


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 4 — FAST CONCAT (lossless, seconds not hours)
# ═════════════════════════════════════════════════════════════════════════════
def phase4_concat(compressed):
    _log("PHASE 4 · Fast lossless concat")

    final = OUTPUT_DIR / "DJ_LOG_FULL_MOVIE.mp4"
    if final.exists():
        final.unlink()

    clist = OUTPUT_DIR / "_concat_parts.txt"
    clist.write_text("\n".join(f"file '{p}'" for p in compressed) + "\n")

    _run([FFMPEG, "-y", "-v", "warning",
          "-f", "concat", "-safe", "0", "-i", str(clist),
          "-c", "copy", "-movflags", "+faststart",
          str(final)], capture=False)

    clist.unlink(missing_ok=True)

    dur = _duration(final)
    sz  = final.stat().st_size / (1024**3)
    _step(f"Full movie: {final.name}  {sz:.2f} GB  {dur/60:.1f} min")
    return final


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 5 — BEST MOMENTS
# ═════════════════════════════════════════════════════════════════════════════
def phase5_best_moments(movie_path):
    _log("PHASE 5 · Finding best moments by audio energy")

    data = _audio_np(movie_path, sr=SYNC_SR)
    win = SYNC_SR * ENERGY_WIN
    n_wins = len(data) // win
    energy = np.array([np.sqrt(np.mean(data[i*win:(i+1)*win]**2)) for i in range(n_wins)])

    kernel = np.ones(SMOOTH_WIN) / SMOOTH_WIN
    smoothed = np.convolve(energy, kernel, mode="same")

    if EDGE_MARGIN > 0:
        smoothed[:EDGE_MARGIN] = 0
    if len(smoothed) > CLIP_DUR + EDGE_MARGIN:
        smoothed[-(EDGE_MARGIN + CLIP_DUR):] = 0

    moments = []
    for _ in range(N_CLIPS):
        if np.max(smoothed) <= 0:
            break
        peak = int(np.argmax(smoothed))
        eng  = float(smoothed[peak])
        start = max(0, peak - CLIP_DUR // 2)
        start = min(start, max(0, n_wins - CLIP_DUR))
        moments.append((int(start), eng))
        smoothed[max(0, peak-MIN_GAP) : min(len(smoothed), peak+MIN_GAP)] = 0

    moments.sort(key=lambda x: x[0])
    _step(f"Selected {len(moments)} best moments:")
    for i, (s, e) in enumerate(moments, 1):
        print(f"      Clip {i:02d}:  {s/60:6.1f} min → {(s+CLIP_DUR)/60:6.1f} min")
    return moments


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 6 — EXPORT CLIPS
# ═════════════════════════════════════════════════════════════════════════════
def phase6_clips(movie, moments):
    _log("PHASE 6 · Exporting clips (IG 4:5 + Normal 16:9)")

    ig_dir  = OUTPUT_DIR / "ig_4x5"
    nm_dir  = OUTPUT_DIR / "normal_16x9"
    ig_dir.mkdir(parents=True, exist_ok=True)
    nm_dir.mkdir(parents=True, exist_ok=True)

    for i, (start, _) in enumerate(moments, 1):
        ig_out = ig_dir / f"clip_{i:02d}_ig.mp4"
        _step(f"Clip {i:02d} IG [{start/60:.1f}m]")
        _run([
            FFMPEG, "-y", "-v", "warning",
            "-ss", str(start), "-t", str(CLIP_DUR),
            "-i", str(movie),
            "-vf", f"scale=-2:{IG_H}:flags=lanczos,crop={IG_W}:{IG_H},format=yuv420p",
            "-c:v", "libx264", "-preset", "slow", "-b:v", CLIP_VIDEO_BR,
            "-maxrate", CLIP_VIDEO_BR, "-bufsize", "7000k",
            "-profile:v", "high", "-level:v", "4.0",
            "-c:a", "aac", "-b:a", AUDIO_BR, "-ac", "2", "-ar", str(AUDIO_SR),
            "-movflags", "+faststart",
            str(ig_out),
        ], capture=False)

        nm_out = nm_dir / f"clip_{i:02d}_normal.mp4"
        _step(f"Clip {i:02d} Normal [{start/60:.1f}m]")
        _run([
            FFMPEG, "-y", "-v", "warning",
            "-ss", str(start), "-t", str(CLIP_DUR),
            "-i", str(movie),
            "-vf", "format=yuv420p",
            "-c:v", "libx264", "-preset", "slow", "-b:v", CLIP_VIDEO_BR,
            "-maxrate", CLIP_VIDEO_BR, "-bufsize", "7000k",
            "-profile:v", "high",
            "-c:a", "aac", "-b:a", AUDIO_BR, "-ac", "2", "-ar", str(AUDIO_SR),
            "-movflags", "+faststart",
            str(nm_out),
        ], capture=False)

    _step(f"{len(moments)} IG clips → {ig_dir}")
    _step(f"{len(moments)} Normal clips → {nm_dir}")


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════
def main():
    print("\n" + "█" * 72)
    print("██  DJ-LOG VIDEO PROCESSOR v2 — Per-Video Pipeline")
    print("██  Sync · Compress (vid by vid) · Concat · Clips")
    print("█" * 72, flush=True)

    t0 = time.time()

    mp4_info, wav_info = phase1_discover()
    if not mp4_info:
        return print("No MP4 files found.")

    sync_map, total_dur = phase2_sync(mp4_info, wav_info)

    compressed = phase3_encode_per_video(sync_map)

    movie = phase4_concat(compressed)

    moments = phase5_best_moments(movie)

    phase6_clips(movie, moments)

    # cleanup partial files
    for f in OUTPUT_DIR.glob("_tmp_*"):
        f.unlink(missing_ok=True)
    # keep part files for now (resumability)

    elapsed = time.time() - t0
    _log("ALL DONE!", char="█")
    print(f"  Total time: {elapsed/60:.1f} min")
    print(f"  Output:     {OUTPUT_DIR}")
    print(f"  Full movie: DJ_LOG_FULL_MOVIE.mp4")
    print(f"  Parts:      part_01..{len(compressed):02d}.mp4 (can delete after verifying)")
    print(f"  IG clips:   ig_4x5/clip_01..{N_CLIPS:02d}_ig.mp4")
    print(f"  Normal:     normal_16x9/clip_01..{N_CLIPS:02d}_normal.mp4\n")


if __name__ == "__main__":
    main()
