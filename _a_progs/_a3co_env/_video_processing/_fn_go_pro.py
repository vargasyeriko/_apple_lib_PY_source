


# -----######-----###### CORE IMPORTABLE FUNCTION (GoPro Progressive Renamer — Fixed Lazy Version) -----######-----######
import os
import re
import shlex
import subprocess
from pathlib import Path
from datetime import datetime
import pandas as pd
from tqdm import tqdm
import shutil


def _video_1308_goproseq_GET_renamed_files(
    inputs,
    base_name,
    video_extensions,
    prefix="_gp",
    start_index=1,
    dry_run=True,
    overwrite=False
):
    """
    Rename GoPro chaptered clips into a single progressive sequence:
      _gp{n}_{base}.ext

    inputs : folder path, list of paths, Series, or DataFrame with 'Path'
    base_name : the {base} in the new names
    video_extensions : list of extensions to accept (case-insensitive)
    dry_run : if True, no files moved, just a plan
    overwrite : if True, overwrite existing target files
    """

    # ---------- helpers ----------
    def _is_iterable_paths(x):
        return isinstance(x, (list, tuple, set)) or (
            hasattr(x, "__iter__") and not isinstance(x, (str, bytes, Path, pd.DataFrame))
        )

    def _normalize_exts(exts):
        return {e.lower() if e.startswith(".") else f".{e.lower()}" for e in exts}

    def _natural_sort_key(p: Path):
        # tuple instead of list to avoid Pandas "unhashable type" error
        s = p.stem
        parts = re.split(r"(\d+)", s)
        return tuple(int(x) if x.isdigit() else x.lower() for x in parts)

    def _ffprobe_creation_time(p: Path):
        cmds = [
            f'ffprobe -v error -select_streams v:0 -show_entries stream_tags=creation_time '
            f'-of default=nk=1:nw=1 {shlex.quote(str(p))}',
            f'ffprobe -v error -show_entries format_tags=creation_time '
            f'-of default=nk=1:nw=1 {shlex.quote(str(p))}',
        ]
        for cmd in cmds:
            try:
                out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True).strip()
                if out:
                    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ",
                                "%Y-%m-%dT%H:%M:%SZ",
                                "%Y-%m-%d %H:%M:%S",
                                "%Y-%m-%dT%H:%M:%S%z"):
                        try:
                            return datetime.strptime(out, fmt)
                        except:
                            pass
            except:
                pass
        return None

    def _gather_paths(inp):
        if isinstance(inp, (str, Path)):
            folder = Path(inp).expanduser().resolve()
            if not folder.exists() or not folder.is_dir():
                raise FileNotFoundError(f"Folder not found: {folder}")
            exts = _normalize_exts(video_extensions)
            return [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in exts]
        elif isinstance(inp, pd.DataFrame):
            if "Path" not in inp.columns:
                raise KeyError("DataFrame must contain a 'Path' column.")
            return [Path(x).expanduser().resolve() for x in inp["Path"].tolist()]
        elif isinstance(inp, pd.Series):
            return [Path(x).expanduser().resolve() for x in inp.tolist()]
        elif _is_iterable_paths(inp):
            return [Path(x).expanduser().resolve() for x in inp]
        else:
            raise TypeError("Unsupported input type for 'inputs'.")

    def _best_timestamp(p: Path):
        dt = _ffprobe_creation_time(p)
        if dt is not None:
            return ("ffprobe", dt)
        try:
            return ("mtime", datetime.fromtimestamp(p.stat().st_mtime))
        except:
            return (None, None)

    # ---------- collect inputs ----------
    paths = _gather_paths(inputs)
    exts = _normalize_exts(video_extensions)
    paths = [p for p in paths if p.exists() and p.suffix.lower() in exts]
    if not paths:
        return pd.DataFrame(columns=["old_path", "new_path", "method_time", "timestamp", "action", "error"])

    # ---------- metadata + sort ----------
    rows = []
    for p in paths:
        method, ts = _best_timestamp(p)
        rows.append({"path": p, "method_time": method, "timestamp": ts})

    df = pd.DataFrame(rows)
    df["nat_key"] = df["path"].apply(_natural_sort_key)
    df["ts_sort"] = df["timestamp"].apply(lambda x: x if isinstance(x, datetime) else datetime.max)
    df = df.sort_values(["ts_sort", "nat_key"], kind="mergesort").reset_index(drop=True)

    # ---------- target names ----------
    mapping = []
    idx = start_index
    for _, r in df.iterrows():
        p = r["path"]
        new_name = f"{prefix}{idx}_{base_name}{p.suffix}"
        mapping.append((p, p.with_name(new_name)))
        idx += 1

    # ---------- apply / dry-run ----------
    results = []
    for old_p, new_p in tqdm(mapping, desc="TQM • Renaming GoPro clips", unit="file"):
        action, err = ("planned", "")
        if new_p.exists() and not overwrite:
            action, err = "skipped_conflict", "target_exists"
        else:
            if not dry_run:
                try:
                    if new_p.exists() and overwrite:
                        new_p.unlink()
                    shutil.move(str(old_p), str(new_p))
                    action = "renamed"
                except Exception as e:
                    action, err = "error", str(e)
        results.append({
            "old_path": str(old_p),
            "new_path": str(new_p),
            "method_time": df.loc[df["path"] == old_p, "method_time"].iloc[0],
            "timestamp": df.loc[df["path"] == old_p, "timestamp"].iloc[0],
            "action": action,
            "error": err
        })

    return pd.DataFrame(results)
# -----######-----###### END CORE FUNCTION -----######-----######

import subprocess, os
from pathlib import Path
from datetime import datetime
import cv2

def _video_0506_pipe_GET_realdata_verifiedrename(folder_path, delete='y'):
    folder = Path(folder_path)
    video_files = sorted(list(folder.rglob("*.mp4")) + list(folder.rglob("*.MP4")))
    if not video_files:
        print("❌ No MP4 files found.")
        return

    print("\n🎬 MOV CONVERSION FOR ENTIRE BATCH?")
    mov_choice = input("💡 Type 'y' to convert all videos to .mov after rename, or press ENTER to skip: ").strip().lower()
    do_mov = mov_choice == 'y'

    for f in video_files:
        print(f"\n📼 Verifying: {f.name}")
        os.system(f'open "{f}"')
        keyword = input("🎤 Enter keyword for this clip (e.g. DJ name, event): ").strip().replace(" ", "_")

        try:
            # --- Get creation time from ffprobe ---
            cmd = [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream_tags=creation_time",
                "-of", "default=noprint_wrappers=1:nokey=0",
                str(f)
            ]
            output = subprocess.check_output(cmd).decode().splitlines()
            creation_line = next((l for l in output if "TAG:creation_time=" in l), None)
            if not creation_line:
                print(f"❌ No creation_time in metadata: {f.name}")
                continue
            creation_time = creation_line.split("=", 1)[1].strip()
            dt = datetime.fromisoformat(creation_time.replace("Z", "+00:00"))

            # --- OpenCV for resolution, fps, frame count ---
            cap = cv2.VideoCapture(str(f))
            if not cap.isOpened():
                print(f"❌ Cannot open video for frame analysis: {f.name}")
                continue

            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()

            if width == 0 or height == 0 or fps == 0:
                print(f"❌ Invalid resolution/FPS for: {f.name}")
                continue

            duration_sec = int(frame_count / fps)
            duration_min = round(duration_sec / 60)

            # --- Aspect ratio label ---
            ratio = round(width / height, 2)
            if abs(ratio - 16/9) < 0.05:
                aspect = "16_9"
            elif abs(ratio - 4/3) < 0.05:
                aspect = "4_3"
            else:
                aspect = str(ratio).replace(".", "_")

            # --- Compose filename ---
            ext = f.suffix.lower()
            fps_label = round(fps)
            base_name = (
                f"vid_{dt.strftime('%Y_%m_%d')}_Hr_{dt.strftime('%H_%M_%S')}_"
                f"Yfram_{fps_label}_Yvres_{width}x{height}_Yaspr_{aspect}_Ydura_{duration_min}_MIN_{keyword}"
            )
            new_path_mp4 = f.with_name(base_name + ext)

            # --- Collision handling ---
            counter = 1
            while new_path_mp4.exists():
                new_path_mp4 = f.with_name(f"{base_name}_no_{counter}{ext}")
                counter += 1

            # --- Rename original file ---
            print(f"\n🔁 Rename:\n→ {f.name} ➡️ {new_path_mp4.name}")
            input("✅ Press ENTER to confirm rename...")
            f.rename(new_path_mp4)
            print(f"✅ Renamed to: {new_path_mp4.name}")

            # --- MOV conversion (if chosen once) ---
            if do_mov:
                new_path_mov = new_path_mp4.with_suffix(".mov")
                print(f"🎞️ Converting to MOV:\n→ {new_path_mov.name}")

                conv_cmd = [
                    "ffmpeg", "-i", str(new_path_mp4),
                    "-c", "copy",
                    str(new_path_mov)
                ]
                subprocess.run(conv_cmd, check=True)
                print(f"✅ MOV created: {new_path_mov.name}")

                if delete.lower() == 'y':
                    new_path_mp4.unlink()
                    print(f"🗑️ Deleted original MP4: {new_path_mp4.name}")

        except Exception as e:
            print(f"❌ Error processing {f.name}: {e}")







# -----######-----###### VIDEO MP4 CHOPPER — ORIGINAL DIMENSIONS -----######-----###### #
from moviepy.editor import VideoFileClip
from pathlib import Path
from tqdm import tqdm
import random

def _video_1408_mp4chop_GET_export_clips(input_folder, duration=60, n_clips=9, custom_length='n', seed=None):
    """
    -----######-----######  MAIN FUNCTION (IMPORTABLE)  -----######-----######
    Purpose:
        Chop each .mp4 in `input_folder` into randomized fixed-length subclips (default 9 × 60s)
        without resizing or cropping. Optionally allow interactive custom cuts if `custom_length='y'`.

    Inputs:
        input_folder  : str | Path  -> folder containing .mp4 files
        duration      : int|float   -> subclip duration in seconds (default 60)
        n_clips       : int         -> number of randomized subclips per video (default 9)
        custom_length : 'y'|'n'     -> if 'y', prompt for custom start-end (in minutes)
        seed          : int|None    -> optional random seed for reproducibility

    Output:
        Returns a short success string after processing. Saves clips in subfolders
        named after each video's stem.
    """
    input_folder = Path(input_folder)
    video_paths = [p for p in input_folder.iterdir() if p.suffix.lower() == '.mp4']

    if not video_paths:
        return "❌ No .mp4 files found in input folder."

    if seed is not None:
        random.seed(seed)

    for video_path in video_paths:
        clip = None
        try:
            clip = VideoFileClip(str(video_path))
            total_duration = float(clip.duration or 0.0)
            usable_range = total_duration - float(duration)

            if usable_range <= 0:
                print(f"⚠️ Skipping {video_path.name} (too short: {total_duration:.2f}s < {duration}s)")
                continue

            output_dir = input_folder / video_path.stem
            output_dir.mkdir(exist_ok=True)

            # --- Generate randomized start times ---
            if n_clips < 1:
                n_clips = 1
            bucket = usable_range / n_clips
            base_points = [bucket * i for i in range(n_clips)]
            random_offsets = [random.uniform(0, max(bucket, 1e-6)) for _ in range(n_clips)]
            start_times = [min(bp + ro, usable_range) for bp, ro in zip(base_points, random_offsets)]

            print(f"\n📤 Processing: {video_path.name}  •  Total: {total_duration:.2f}s  •  Clips: {n_clips} × {duration}s")

            # Fixed-length chops
            for i, start_time in tqdm(
                list(enumerate(start_times, start=1)),
                total=n_clips,
                desc=f"⏳ {video_path.stem[:20]}"
            ):
                end_time = min(start_time + duration, total_duration)
                if end_time - start_time <= 0.5:
                    continue

                subclip = clip.subclip(start_time, end_time)
                out_path = output_dir / f"{video_path.stem}_{i:02}.mp4"
                subclip.write_videofile(
                    str(out_path),
                    codec="libx264",
                    audio_codec="aac",
                    verbose=False,
                    logger=None
                )
                subclip.close()

            print(f"✅ {n_clips} clips saved for: {video_path.stem}")

            # --- Custom Cut Prompt ---
            if custom_length == 'y':  # Only ask if explicitly set to 'y'
                custom_index = 1
                while True:
                    range_str = input("🕐 Enter start-end in minutes (e.g. 1.2 - 3.2), or ENTER to finish: ").strip()
                    if not range_str:
                        break

                    try:
                        for sep in ["–", "—", "to"]:
                            range_str = range_str.replace(sep, "-")
                        start_min, end_min = [float(x.strip()) for x in range_str.split("-")]
                        start_sec = start_min * 60
                        end_sec = end_min * 60

                        if end_sec > total_duration or start_sec >= end_sec:
                            print("❌ Invalid range. Try again.")
                            continue

                        subclip = clip.subclip(start_sec, end_sec)
                        out_path = output_dir / f"custom_{video_path.stem}_{custom_index}.mp4"
                        subclip.write_videofile(
                            str(out_path),
                            codec="libx264",
                            audio_codec="aac",
                            verbose=False,
                            logger=None
                        )
                        subclip.close()
                        print(f"✅ Custom clip saved: {out_path.name}")
                        custom_index += 1

                    except Exception as e:
                        print(f"❌ Error parsing input: {e}")
                        continue

        finally:
            if clip:
                clip.close()

    return "✅ All .mp4 videos chopped with optional custom cuts."



################ get chops story SIZE 

# -----######-----###### IG PORTRAIT CHOPPER w/ CUSTOM CUTS (STORY FLOW FIX) -----######-----###### #
from moviepy.editor import VideoFileClip
from pathlib import Path
from tqdm import tqdm
import random

def _video_story_mp4(input_folder, duration=60, x_offset_percent=0, custom='n'):
    """
    Keeps your original behavior (resize to 1920 tall, crop to 1080 wide),
    exports 9 randomized portrait clips, then (optionally) asks for custom ranges
    for EVERY video when custom='y'. Minimal changes to your structure and outputs.
    """
    input_folder = Path(input_folder)
    video_paths = [p for p in input_folder.iterdir() if p.suffix.lower() == '.mp4']

    if not video_paths:
        return "❌ No .mp4 files found in input folder."

    for video_path in video_paths:
        clip = VideoFileClip(str(video_path))
        total_duration = clip.duration
        usable_range = total_duration - duration

        if usable_range <= 0:
            print(f"⚠️ Skipping {video_path.name} (too short)")
            clip.close()
            continue

        output_dir = input_folder / video_path.stem
        output_dir.mkdir(exist_ok=True)

        # IG Story dimensions
        ig_width = 1080
        ig_height = 1920

        # Resize to 1920 height (portrait mode)
        resized_clip = clip.resize(height=ig_height)
        video_width = resized_clip.w

        # Horizontal crop shift based on % offset
        x_offset_percent = max(-100, min(100, x_offset_percent))
        max_shift = (video_width - ig_width) / 2
        x_shift = x_offset_percent / 100 * max_shift
        x_center = (video_width / 2) + x_shift

        # Generate 9 smart cut points
        base_points = [usable_range * i / 9 for i in range(9)]
        random_offsets = [random.uniform(0, usable_range / 9) for _ in range(9)]
        start_times = [min(bp + ro, usable_range) for bp, ro in zip(base_points, random_offsets)]

        print(f"\n📤 Processing: {video_path.name}")
        for i, start_time in tqdm(
            list(enumerate(start_times)),
            total=9,
            desc=f"⏳ {video_path.stem[:20]}",
            leave=False  # <- ensure clean termination before input prompts
        ):
            subclip = resized_clip.subclip(start_time, start_time + duration)
            cropped = subclip.crop(x_center=x_center, width=ig_width)
            out_path = output_dir / f"{video_path.stem}_story_{i+1:02}.mp4"
            cropped.write_videofile(
                str(out_path),
                codec="libx264",
                audio_codec="aac",
                verbose=False,
                logger=None
            )
            subclip.close()
            cropped.close()

        print(f"✅ 9 IG story clips saved for: {video_path.stem}")

        # --- Custom Cut Prompt (per video) ---
        if custom == 'y':
            print("")  # newline to separate from tqdm line
            custom_index = 1
            while True:
                range_str = input("🕐 Enter start-end in minutes (e.g. 1.2 - 3.2), or ENTER to skip: ").strip()
                if not range_str:
                    break
                try:
                    # Allow separators like '–' '—' and 'to'
                    for sep in ["–", "—", "to"]:
                        range_str = range_str.replace(sep, "-")
                    start_min, end_min = [float(x.strip()) for x in range_str.split("-")]
                    start_sec = start_min * 60
                    end_sec = end_min * 60

                    if end_sec > total_duration or start_sec >= end_sec:
                        print("❌ Invalid range. Try again.")
                        continue

                    subclip = resized_clip.subclip(start_sec, end_sec)
                    cropped = subclip.crop(x_center=x_center, width=ig_width)
                    out_path = output_dir / f"__custom_{video_path.stem}_{custom_index}.mp4"
                    cropped.write_videofile(
                        str(out_path),
                        codec="libx264",
                        audio_codec="aac",
                        verbose=False,
                        logger=None
                    )
                    subclip.close()
                    cropped.close()
                    print(f"✅ Custom clip saved: {out_path.name}")
                    custom_index += 1

                except Exception as e:
                    print(f"❌ Error parsing input: {e}")
                    continue

        # Close per-video resources
        resized_clip.close()
        clip.close()

    return "✅ All .mp4 videos exported in IG story format with optional custom cuts."





############## get final VIDEO 

# -----######-----###### VIDEO GP MERGE + MP3 (FIRST-LEVEL ONLY) — TQM -----######-----###### #
from moviepy.editor import VideoFileClip, concatenate_videoclips
from pathlib import Path
from tqdm import tqdm
import re, sys

# External knobs (adjust outside the function as you like)
VIDEO_GLOB_PATTERN = "*.mp4"   # first-level only — do not recurse
GP_TOKEN_PATTERN   = r'gp(\d+)'  # case-insensitive; e.g., gp1, GP2, Gp10
RESIZE_RATIO       = 0.65      # 65% of original resolution
VIDEO_BITRATE      = "1500k"   # recommended sweet spot
THREADS            = 4         # ffmpeg threads
AUDIO_MP3_BITRATE  = "128k"    # final MP3 bitrate


# ===== MAIN IMPORTABLE FUNCTION =====
def _video_1408_gpmerge_GET_paths_video_audio(folder_path):
    """
    Scan only the FIRST LEVEL of `folder_path` for .mp4 files whose names contain a 'gp#' token (e.g., gp1, gp2).
    Order clips by gp#, compress each to .mov (65% size, 1500k), merge to a single MOV, then extract MP3.
    Returns: (final_video_path, final_audio_path) or None on early exit.
    """

    # ---------- TQM: Discover ----------
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        print("❌ Folder not found or not a directory.")
        return

    print("TQM • Scanning first-level MP4 files…")
    sys.stdout.flush()

    # first-level only (no recursion)
    candidates = sorted(folder.glob(VIDEO_GLOB_PATTERN))

    # Parse gp# token
    gp_items = []
    rx = re.compile(GP_TOKEN_PATTERN, flags=re.IGNORECASE)
    for p in candidates:
        m = rx.search(p.name)
        if m:
            try:
                gp_num = int(m.group(1))
                gp_items.append((gp_num, p))
            except ValueError:
                pass  # ignore malformed numbers

    if not gp_items:
        print("❌ No files with a 'gp#' token (e.g., gp1, gp2) were found at the first level.")
        return

    # Order by gp#, then by name for tie-breakers
    gp_items.sort(key=lambda t: (t[0], t[1].name.lower()))
    ordered_files = [p for _, p in gp_items]

    # ---------- TQM: Preview order ----------
    print("\n🧾 Proposed progression order (by gp#):")
    for i, p in enumerate(ordered_files, 1):
        print(f"{i:02d}. gp{re.search(rx, p.name).group(1):>2}  —  {p.name}")
        sys.stdout.flush()

    input("\n❓ Is this the correct progression? (Press ENTER to continue or Ctrl+C to abort): ")

    # ---------- TQM: Compress each to MOV ----------
    temp_movs = []
    print("\nTQM • Step 1/3 — Compressing MP4 → MOV @ 65% / 1500k")
    for vid in tqdm(ordered_files, desc="🎬 Compressing", unit="file"):
        clip = VideoFileClip(str(vid))
        new_w = max(1, int(clip.w * RESIZE_RATIO))
        new_h = max(1, int(clip.h * RESIZE_RATIO))
        clip_resized = clip.resize(newsize=(new_w, new_h))

        out_path = vid.with_name(vid.stem + "_compressed.mov")
        clip_resized.write_videofile(
            str(out_path),
            codec='libx264',
            audio_codec='aac',
            bitrate=VIDEO_BITRATE,
            preset='ultrafast',
            ffmpeg_params=["-movflags", "faststart"],
            threads=THREADS,
            logger=None
        )
        temp_movs.append(out_path)

        # ensure resources are closed
        try:
            clip_resized.close()
        finally:
            try:
                clip.close()
            except:
                pass

    # ---------- TQM: Merge MOVs ----------
    print("\nTQM • Step 2/3 — Merging MOV files…")
    sys.stdout.flush()
    clips = []
    try:
        for m in tqdm(temp_movs, desc="📦 Loading for merge", unit="file"):
            clips.append(VideoFileClip(str(m)))

        final_video_path = folder / "final_merged_video.mov"
        final_clip = concatenate_videoclips(clips, method="compose")
        final_clip.write_videofile(
            str(final_video_path),
            codec='libx264',
            audio_codec='aac',
            bitrate=VIDEO_BITRATE,
            preset='ultrafast',
            ffmpeg_params=["-movflags", "faststart"],
            threads=THREADS,
            logger=None
        )
    finally:
        # close merge clips
        for c in clips:
            try:
                c.close()
            except:
                pass
        try:
            final_clip.close()
        except:
            pass

    # ---------- TQM: Clean temps ----------
    print("\nTQM • Housekeeping — Deleting temporary MOV files…")
    for tmp in tqdm(temp_movs, desc="🧹 Deleting", unit="file"):
        try:
            tmp.unlink(missing_ok=True)
        except:
            pass

    # ---------- TQM: Extract MP3 ----------
    print("\nTQM • Step 3/3 — Extracting MP3 from merged MOV…")
    final_audio_path = final_video_path.with_suffix(".mp3")
    merged_v = VideoFileClip(str(final_video_path))
    try:
        audio = merged_v.audio
        if audio is None:
            print("⚠️  No audio stream detected. Skipping MP3 extraction.")
            final_audio_path = None
        else:
            audio.write_audiofile(str(final_audio_path), bitrate=AUDIO_MP3_BITRATE, logger=None)
            try:
                audio.close()
            except:
                pass
    finally:
        try:
            merged_v.close()
        except:
            pass

    print("\n✅ All done!")
    print(f"🎞 Final video: {final_video_path.name}")
    if final_audio_path:
        print(f"🎧 Extracted audio: {final_audio_path.name}")

    return final_video_path, final_audio_path
# -----######-----###### END MAIN FUNCTION -----######-----###### #
# -----######-----###### VIDEO RENAME: GOPRO SEQ + VERIFIED METADATA v1.0 — LIVE TQM -----######-----###### #


# -----######-----###### GOPRO GP CONCAT + MP3 EXTRACT v1.0 — LIVE TQM -----######-----###### #
# -----######-----###### GOPRO GP CONCAT + MP3 EXTRACT — YOUR NAMES, LIVE TQM -----######-----###### #
# -----######-----###### GOPRO — CONCAT ALL *_gpN MP4 INTO ONE MOVIE — LIVE TQM -----######-----###### #
# -----######-----###### GOPRO — CONFIRM PROGRESSION THEN CONCAT MOVIE — LIVE TQM -----######-----###### #
import os, re, shlex, subprocess, tempfile, shutil
from pathlib import Path
from tqdm import tqdm
from datetime import datetime

# Timestamp in your style (optional): vid_YYYY_MM_DD_Hr_HH_MM_SS ...
_TS_RE = re.compile(r"vid_(\d{4})_(\d{2})_(\d{2})_Hr_(\d{2})_(\d{2})_(\d{2})", re.IGNORECASE)

# Find _gpN anywhere in the stem (not only at the end)
_GP_ANY_RE = re.compile(r"(?i)_gp(\d+)")


def _parse_dt_from_name(stem):
    m = _TS_RE.search(stem)
    if not m:
        return None
    Y, M, D, h, mnt, s = map(int, m.groups())
    try:
        return datetime(Y, M, D, h, mnt, s)
    except Exception:
        return None


def _extract_gpnum_anywhere(stem):
    """
    Return the LAST gp number found in the name (e.g., ..._foo_gp1_bar_gp2 -> 2),
    or None if not found.
    """
    found = [int(x.group(1)) for x in _GP_ANY_RE.finditer(stem)]
    return found[-1] if found else None


def _safe_concat_list(paths):
    """Create concat list file for ffmpeg; return Path."""
    tf = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    with tf as f:
        for p in paths:
            safe_path = p.as_posix().replace("'", "'\\''")  # safe for ffmpeg concat list
            f.write(f"file '{safe_path}'\n")
    return Path(tf.name)


# -----###### MAIN IMPORTABLE FUNCTION (ADD TO YOUR LIB) #####----- #
def _video_together_and_mp3(folder_path):
    """
    Input:
        folder_path : str/Path — scan ONLY first-level .mp4 files.

    Flow:
        - Collect all .mp4 in the folder (no subfolders).
        - Detect gp numbers anywhere in the filename (e.g., ..._gp1..., ..._gp2...).
        - Sort by (timestamp in name if present else mtime) THEN by gp number (if present) THEN by name.
        - PRINT the proposed progression and ASK for confirmation [y/N].
        - If confirmed, CONCAT losslessly (-c copy) into ONE MP4.
        - No MP3 extraction in this function.

    Output:
        dict: {'out_mp4': '<path>', 'parts': [<paths...>]} or None if aborted/failure.

    Requires:
        ffmpeg in PATH (macOS: brew install ffmpeg)
    """
    folder = Path(folder_path).expanduser().resolve()
    if not folder.is_dir():
        print(f"❌ Folder not found: {folder}")
        return None

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("❌ ffmpeg not found in PATH. Install: brew install ffmpeg")
        return None

    # 1) Gather top-level mp4s
    vids = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".mp4"]
    if not vids:
        print("❗ No .mp4 files found in the top level of this folder.")
        return None

    # 2) Build sort keys
    sortable = []
    for p in vids:
        stem = p.stem
        dt = _parse_dt_from_name(stem) or datetime.fromtimestamp(p.stat().st_mtime)
        gp = _extract_gpnum_anywhere(stem)
        sortable.append((dt, gp if gp is not None else 0, p.name.lower(), p, gp))

    # 3) Sort by (dt, gp, name)
    sortable.sort(key=lambda t: (t[0], t[1], t[2]))
    ordered = [t[3] for t in sortable]

    # 4) Show proposed progression and ASK
    print("\n🔎 Proposed progression (top-level only):")
    for i, (_, _, _, p, gp) in enumerate(sortable, 1):
        tag = f"gp={gp}" if gp is not None else "gp=?"
        print(f"  [{i:02d}] {tag}  —  {p.name}")

    ans = input("\n❓ Is this the right progression? [y/N]: ").strip().lower()
    if ans != "y" and ans != "yes":
        print("⛔ Aborted by user. No movie created.")
        return None

    # 5) Derive output name from first file; replace trailing _gpN with _ALL, else add _ALL
    first_stem = ordered[0].stem
    stem_all = re.sub(r"(?i)_gp\d+\b", "_ALL", first_stem)
    if stem_all == first_stem:
        stem_all = f"{first_stem}_ALL"
    out_mp4 = folder / f"__final_{stem_all}.mp4"

    # 6) Build concat list + run ffmpeg
    list_path = _safe_concat_list(ordered)

    pbar = tqdm(total=1, bar_format="TQM • {l_bar}{bar} | {n_fmt}/{total_fmt} step")
    try:
        if out_mp4.exists():
            out_mp4.unlink()

        cmd_concat = (
            f"{shlex.quote(ffmpeg)} -hide_banner -y "
            f"-f concat -safe 0 -i {shlex.quote(str(list_path))} "
            f"-c copy {shlex.quote(str(out_mp4))}"
        )
        print(f"\n▶️ Concatenating {len(ordered)} part(s) → {out_mp4.name}")
        rc = subprocess.run(cmd_concat, shell=True).returncode
        if rc != 0 or not out_mp4.exists():
            print("❌ ffmpeg concat failed.")
            return None

        pbar.update(1)
        print("✅ Movie created.")
        return {"out_mp4": str(out_mp4), "parts": [str(p) for p in ordered]}

    finally:
        pbar.close()
        try:
            if list_path.exists():
                list_path.unlink()
        except Exception:
            pass
