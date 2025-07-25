# -----######-----###### ULTRA VERIFIED RENAME + MOV CONVERSION -----######-----######
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
            print(f"\n🔁 Verified Rename:\n→ {f.name} ➡️ {new_path_mp4.name}")
            input("✅ Press ENTER to confirm rename and convert to .mov...")
            f.rename(new_path_mp4)
            print(f"✅ Renamed to: {new_path_mp4.name}")

            # --- MOV conversion ---
            new_path_mov = new_path_mp4.with_suffix(".mov")
            print(f"🎞️ Converting to MOV:\n→ {new_path_mov.name}")

            conv_cmd = [
                "ffmpeg", "-i", str(new_path_mp4),
                "-c", "copy",
                str(new_path_mov)
            ]
            subprocess.run(conv_cmd, check=True)
            print(f"✅ MOV created: {new_path_mov.name}")

            # --- Optional deletion ---
            if delete.lower() == 'y':
                new_path_mp4.unlink()
                print(f"🗑️ Deleted original MP4: {new_path_mp4.name}")

        except Exception as e:
            print(f"❌ Error processing {f.name}: {e}")
###########


############ ## RE - SAMPLE - 60-90 SEC CLIPS - STORY SIZE IG

# -----######-----###### MOV CENTER CROP via PARAM + 9 CLIPS + CUSTOM -----######-----######
# -----######-----###### 9:16 IG STORIES — MOV CUTTER + OFFSET -----######-----######
from moviepy.editor import VideoFileClip
from pathlib import Path
from tqdm import tqdm
import random

def _video_story(input_folder, duration=60, x_offset_percent=0):
    input_folder = Path(input_folder)
    video_paths = [p for p in input_folder.iterdir() if p.suffix.lower() == '.mov']

    if not video_paths:
        return "❌ No .mov files found in input folder."

    for video_path in video_paths:
        clip = VideoFileClip(str(video_path))
        total_duration = clip.duration
        usable_range = total_duration - duration

        if usable_range <= 0:
            print(f"⚠️ Skipping {video_path.name} (too short)")
            continue

        output_dir = input_folder / video_path.stem
        output_dir.mkdir(exist_ok=True)

        # IG Story size constants
        ig_width = 1080
        ig_height = 1920

        # Resize to portrait height first
        resized_clip = clip.resize(height=ig_height)
        video_width = resized_clip.w

        # Clip offset param
        x_offset_percent = max(-100, min(100, x_offset_percent))
        max_shift = (video_width - ig_width) / 2
        x_shift = x_offset_percent / 100 * max_shift
        x_center = (video_width / 2) + x_shift

        # Generate 9 random cut points
        base_points = [usable_range * i / 9 for i in range(9)]
        random_offsets = [random.uniform(0, usable_range / 9) for _ in range(9)]
        start_times = [min(bp + ro, usable_range) for bp, ro in zip(base_points, random_offsets)]

        print(f"\n📤 Processing: {video_path.name}")
        for i, start_time in tqdm(enumerate(start_times), total=9, desc=f"⏳ {video_path.stem[:20]}"):
            subclip = resized_clip.subclip(start_time, start_time + duration)
            cropped = subclip.crop(x_center=x_center, width=ig_width)
            out_path = output_dir / f"{video_path.stem}_story_{i+1:02}.mp4"
            cropped.write_videofile(str(out_path), codec="libx264", audio_codec="aac", verbose=False, logger=None)

        print(f"✅ 9 IG story clips saved for: {video_path.stem}")

        # --- Custom Cut Mode ---
        custom_index = 1
        while True:
            response = input(f"✂️  Export custom cut from {video_path.name}? (y/n): ").strip().lower()
            if response != 'y':
                break

            range_str = input("🕐 Enter start-end in minutes (e.g. 1.2 - 3.2): ").strip()
            try:
                start_min, end_min = [float(x.strip()) for x in range_str.split("-")]
                start_sec = start_min * 60
                end_sec = end_min * 60

                if end_sec > total_duration or start_sec >= end_sec:
                    print("❌ Invalid range. Try again.")
                    continue

                subclip = resized_clip.subclip(start_sec, end_sec)
                cropped = subclip.crop(x_center=x_center, width=ig_width)
                out_path = output_dir / f"__custom_{video_path.stem}_{custom_index}.mp4"
                cropped.write_videofile(str(out_path), codec="libx264", audio_codec="aac", verbose=False, logger=None)
                print(f"✅ Custom clip saved: {out_path.name}")
                custom_index += 1

            except Exception as e:
                print(f"❌ Error parsing input: {e}")
                continue

    return "✅ All videos exported in 9:16 IG format, with optional custom cuts."
