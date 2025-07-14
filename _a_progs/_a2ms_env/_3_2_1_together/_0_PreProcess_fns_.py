# # ----------------------------######----------------------------#
# #   _rename_1307_kwtagging_GET_singlefile_interactive_v4       #
# # ----------------------------######----------------------------#

# import os
# from datetime import datetime
# import pandas as pd

# # Month mapping for friendly input
# month_mapping = {
#     "jan": "01", "january": "01",
#     "feb": "02", "february": "02",
#     "mar": "03", "march": "03", "marz": "03",
#     "apr": "04", "april": "04",
#     "may": "05",
#     "jun": "06", "june": "06",
#     "jul": "07", "july": "07",
#     "aug": "08", "august": "08",
#     "sep": "09", "september": "09",
#     "oct": "10", "october": "10",
#     "nov": "11", "november": "11",
#     "dec": "12", "december": "12"
# }

# # ----------------------------######----------------------------#
# #        Utility: Input Date With Confirmed Format             #
# # ----------------------------######----------------------------#
# def input_date_and_confirm():
#     while True:
#         month_input = input("📅 Enter the month (e.g., Jan, February): ").lower()
#         day_input = input("📅 Enter the day (DD): ")
#         year = input("📅 Enter the year (YYYY): ")

#         month = month_mapping.get(month_input[:3], "Invalid")

#         if month == "Invalid":
#             print("❌ Invalid month entered. Please try again.")
#             continue

#         try:
#             day = f"{int(day_input):02d}"
#         except:
#             print("❌ Invalid day. Try again.")
#             continue

#         formatted_date = f"{year}_{month}_{day}"
#         confirm = input(f"✅ Is this date correct? (Y/N) {formatted_date}: ").lower()
#         if confirm == 'y':
#             print(f"✅ Confirmed date: {formatted_date}")
#             return formatted_date
#         else:
#             print("🔁 Let's try again.")

# # ----------------------------######----------------------------#
# #             Utility: String Sanitizer for Safe Use           #
# # ----------------------------######----------------------------#
# def clean(s):
#     return (
#         str(s)
#         .replace(" ", "_").replace("/", "___").replace(",", "_")
#         .replace("(", "").replace(")", "").replace("!", "")
#         .replace("&", "and").replace("’", "").replace("'", "")
#         .replace("¿", "").replace("¡", "").replace(":", "")
#         .replace(";", "").strip()
#     )

# # ----------------------------######----------------------------#
# #      Main Function: Rename File with Only User Fields        #
# # ----------------------------######----------------------------#
# def _rename_1307_kwtagging_GET_singlefile_interactive_v4(file_path):
#     """
#     Renames a single audio file using kw-tag structure.
#     Only uses values explicitly entered by the user.
#     Nothing is assumed (e.g., mix type, purchase date).
#     """

#     if not os.path.isfile(file_path):
#         print("❌ File not found.")
#         return None

#     base_name = os.path.splitext(os.path.basename(file_path))[0]
#     ext = os.path.splitext(file_path)[1]

#     print(f"\n🎵 Default Track Title from filename: {base_name}\n")

#     # Only Track Title is pre-filled
#     overrides = {"Track Title": base_name}

#     # Fields the user can optionally define
#     editable_fields = [
#         "Artist", "Mix Type", "Key", "BPM", "Genre",
#         "Label", "Release Date", "Purchase Date"
#     ]

#     for i, field in enumerate(editable_fields):
#         print(f"{i+2}. {field}")  # starts at 2, since Track Title is 1

#     # User input loop
#     while True:
#         modify = input("\n🔁 Enter numbers of fields to override (comma-separated), or 'n' to skip: ").strip()
#         if modify.lower() == 'n':
#             break
#         selected_fields = [int(i)-1 for i in modify.split(",") if i.strip().isdigit()]
#         for idx in selected_fields:
#             if 1 <= idx < len(editable_fields) + 1:
#                 field = editable_fields[idx - 1]
#                 if "Date" in field:
#                     overrides[field] = input_date_and_confirm()
#                 else:
#                     val = input(f"📝 Enter value for '{field}': ").strip()
#                     if val:
#                         overrides[field] = clean(val)
#         confirm = input("✅ Done editing fields? (y/n): ").lower()
#         if confirm == 'y':
#             break

#     # Fill missing fields with NA
#     for f in editable_fields:
#         if f not in overrides:
#             overrides[f] = "NA"

#     # Build new filename
#     new_name = (
#         f"TRkw_{overrides['Track Title'][:25]}"
#         f"_ARkw_{overrides['Artist'][:25]}"
#         f"_MXkw_{overrides['Mix Type']}"
#         f"_KYkw_{overrides['Key']}"
#         f"_BPkw_{overrides['BPM']}"
#         f"_GNkw_{overrides['Genre']}"
#         f"_LBkw_{overrides['Label']}"
#         f"_RYkw_{overrides['Release Date']}"
#         f"_PYkw_{overrides['Purchase Date']}{ext}"
#     )

#     if len(new_name) > 240:
#         new_name = new_name[:230] + ext

#     new_path = os.path.join(os.path.dirname(file_path), new_name)

#     try:
#         os.rename(file_path, new_path)
#         print(f"\n✅ File successfully renamed to:\n📁 {new_name}")
#         return new_path
#     except Exception as e:
#         print(f"❌ Rename failed: {e}")
#         return None
# ########################################### 
# ----------------------------######----------------------------#
#   _rename_1307_kwtagging_GET_singlefile_interactive_v4       #
# ----------------------------######----------------------------#

import os
from datetime import datetime
import pandas as pd

# ----------------------------######----------------------------#
#                  Month Abbreviation Mapping                  #
# ----------------------------######----------------------------#
month_mapping = {
    "jan": "01", "january": "01",
    "feb": "02", "february": "02",
    "mar": "03", "march": "03", "marz": "03",
    "apr": "04", "april": "04",
    "may": "05",
    "jun": "06", "june": "06",
    "jul": "07", "july": "07",
    "aug": "08", "august": "08",
    "sep": "09", "september": "09",
    "oct": "10", "october": "10",
    "nov": "11", "november": "11",
    "dec": "12", "december": "12"
}

# ----------------------------######----------------------------#
#        Utility: Input Date With Confirmed Format             #
# ----------------------------######----------------------------#
def input_date_and_confirm():
    while True:
        month_input = input("📅 Enter the month (e.g., Jan, February): ").lower()
        day_input = input("📅 Enter the day (DD): ")
        year = input("📅 Enter the year (YYYY): ")

        month = month_mapping.get(month_input[:3], "Invalid")

        if month == "Invalid":
            print("❌ Invalid month entered. Please try again.")
            continue

        try:
            day = f"{int(day_input):02d}"
        except:
            print("❌ Invalid day. Try again.")
            continue

        formatted_date = f"{year}_{month}_{day}"
        confirm = input(f"✅ Is this date correct? (Y/N) {formatted_date}: ").lower()
        if confirm == 'y':
            print(f"✅ Confirmed date: {formatted_date}")
            return formatted_date
        else:
            print("🔁 Let's try again.")

# ----------------------------######----------------------------#
#               Utility: Clean + Format Safe String            #
# ----------------------------######----------------------------#
def clean(s):
    return (
        str(s)
        .replace(" ", "_").replace("/", "___").replace(",", "_")
        .replace("(", "").replace(")", "").replace("!", "")
        .replace("&", "and").replace("’", "").replace("'", "")
        .replace("¿", "").replace("¡", "").replace(":", "")
        .replace(";", "").strip()
    )

# ----------------------------######----------------------------#
#       Main Rename + DF Function (No Assumptions)             #
# ----------------------------######----------------------------#
def _rename_1307_kwtagging_GET_singlefile_interactive_v4(file_path):
    """
    Interactively renames a single audio file using kw-tag structure.
    Only uses values explicitly entered by user (no assumptions).
    After renaming, returns a DataFrame with original and new path.
    """

    if not os.path.isfile(file_path):
        print("❌ File not found.")
        return pd.DataFrame(columns=['Original_Path', 'Path'])

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    ext = os.path.splitext(file_path)[1]

    print(f"\n🎵 Default Track Title from filename: {base_name}\n")

    overrides = {"Track Title": base_name}

    editable_fields = [
        "Artist", "Mix Type", "Key", "BPM", "Genre",
        "Label", "Release Date", "Purchase Date"
    ]

    # Show editable options
    for i, field in enumerate(editable_fields):
        print(f"{i+2}. {field}")  # Track Title is #1 by default

    # Prompt for overrides
    while True:
        modify = input("\n🔁 Enter numbers of fields to override (comma-separated), or 'n' to skip: ").strip()
        if modify.lower() == 'n':
            break
        selected_fields = [int(i)-1 for i in modify.split(",") if i.strip().isdigit()]
        for idx in selected_fields:
            if 1 <= idx < len(editable_fields) + 1:
                field = editable_fields[idx - 1]
                if "Date" in field:
                    overrides[field] = input_date_and_confirm()
                else:
                    val = input(f"📝 Enter value for '{field}': ").strip()
                    if val:
                        overrides[field] = clean(val)
        confirm = input("✅ Done editing fields? (y/n): ").lower()
        if confirm == 'y':
            break

    # Set NA for untouched fields
    for f in editable_fields:
        if f not in overrides:
            overrides[f] = "NA"

    # Final filename
    new_name = (
        f"TRkw_{overrides['Track Title'][:25]}"
        f"_ARkw_{overrides['Artist'][:25]}"
        f"_MXkw_{overrides['Mix Type']}"
        f"_KYkw_{overrides['Key']}"
        f"_BPkw_{overrides['BPM']}"
        f"_GNkw_{overrides['Genre']}"
        f"_LBkw_{overrides['Label']}"
        f"_RYkw_{overrides['Release Date']}"
        f"_PYkw_{overrides['Purchase Date']}{ext}"
    )

    if len(new_name) > 240:
        new_name = new_name[:230] + ext

    new_path = os.path.join(os.path.dirname(file_path), new_name)

    try:
        os.rename(file_path, new_path)
        print(f"\n✅ File successfully renamed to:\n📁 {new_name}")
    except Exception as e:
        print(f"❌ Rename failed: {e}")
        return pd.DataFrame(columns=['Original_Path', 'Path'])

    return pd.DataFrame([{
        "Original_Path": file_path,
        "Path": new_path
    }])



################## CAI_1 >>  to AIFF and cover image 

# ----------------------------######----------------------------#
#  _convert_1307_dfwav_GET_mp3_from_wav_with_tags_and_cover   #
# ----------------------------######----------------------------#
# ----------------------------######----------------------------#
#   _convert_1307_dfwav_GET_mp3_from_wav_with_metadata_cover   #
# ----------------------------######----------------------------#
# ----------------------------######----------------------------#
#      _convert_1307_dfwav_GET_clean_aiff_with_tags            #
# ----------------------------######----------------------------#
# ----------------------------######----------------------------#
#      _convert_1307_dfwav_GET_clean_aiff_with_tags            #
# ----------------------------######----------------------------#

# ----------------------------######----------------------------#
#      _convert_1307_dfwav_GET_clean_aiff_with_tags            #
# ----------------------------######----------------------------#

from pathlib import Path
from mutagen.aiff import AIFF
from mutagen.id3 import TIT2, TPE1, TALB, TCON, TDRC, COMM
import subprocess
import pandas as pd
import os
import json

def _extract_tags_ffprobe(wav_path):
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", str(wav_path)
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        tags = data.get("format", {}).get("tags", {})
        return {
            "title": tags.get("title", ""),
            "artist": tags.get("artist", ""),
            "album": tags.get("album", ""),
            "genre": tags.get("genre", ""),
            "year": tags.get("date", "") or tags.get("year", ""),
            "comment": tags.get("comment", "")
        }
    except Exception as e:
        print(f"⚠️ Failed to extract tags from {wav_path.name}: {e}")
        return {}

def _convert_1307_dfwav_GET_clean_aiff_with_tags(df):
    new_paths = []

    for path in df['Path']:
        path = Path(path).expanduser()
        if not path.exists():
            print(f"❌ File not found: {path}")
            new_paths.append(None)
            continue

        ext = path.suffix.lower()
        if ext == ".aiff":
            print(f"⚠️ Already AIFF: {path.name}")
            new_paths.append(str(path))
            continue
        elif ext != ".wav":
            print(f"⚠️ Not a WAV file: {path.name}")
            new_paths.append(None)
            continue

        # Extract metadata
        tags = _extract_tags_ffprobe(path)

        # Convert WAV ➜ AIFF (16-bit, 44.1kHz)
        aiff_path = path.with_suffix('.aiff')
        subprocess.run([
            "ffmpeg", "-y", "-i", str(path),
            "-ar", "44100", "-ac", "2", "-sample_fmt", "s16",
            str(aiff_path)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Apply metadata
        try:
            audio = AIFF(str(aiff_path))
            audio.delete()

            if tags.get("title"):   audio["TIT2"] = TIT2(encoding=3, text=tags["title"])
            if tags.get("artist"):  audio["TPE1"] = TPE1(encoding=3, text=tags["artist"])
            if tags.get("album"):   audio["TALB"] = TALB(encoding=3, text=tags["album"])
            if tags.get("genre"):   audio["TCON"] = TCON(encoding=3, text=tags["genre"])
            if tags.get("year"):    audio["TDRC"] = TDRC(encoding=3, text=tags["year"])
            if tags.get("comment"): audio["COMM::eng"] = COMM(encoding=3, lang='eng', desc='', text=tags["comment"])

            audio.save()
            print(f"✅ Converted + tagged: {aiff_path.name}")
        except Exception as e:
            print(f"⚠️ Failed to tag {aiff_path.name}: {e}")

        # Delete the original WAV file
        try:
            os.remove(path)
            print(f"🗑️ Deleted original WAV: {path.name}")
        except Exception as e:
            print(f"❌ Failed to delete WAV: {path.name} — {e}")

        new_paths.append(str(aiff_path))

    df['Path_aiff'] = new_paths
    print("✅ All done. AIFF files created ➜ tagged ➜ WAVs deleted.")
    return df



############################### CAI 2 chop chop 

# ----------------------------######----------------------------#
#       _aiff_1310_splitter_GET_smart_chunks_dfchunks          #
# ----------------------------######----------------------------#
# ----------------------------######----------------------------#
#       _aiff_1310_splitter_GET_smart_chunks_dfchunks          #
# ----------------------------######----------------------------#
# ----------------------------######----------------------------#
#       _aiff_1310_splitter_GET_smart_chunks_dfchunks          #
# ----------------------------######----------------------------#

# import os
# import numpy as np
# import librosa
# import soundfile as sf
# from mutagen.aiff import AIFF
# from mutagen.id3 import ID3, ID3NoHeaderError
# import pandas as pd
# from tqdm import tqdm

# def _aiff_1310_splitter_GET_smart_chunks_dfchunks(df, mode="medium"):
#     chunk_paths = []

#     # Mode to chunk goal map
#     goal_per_10min = {"low": 3, "medium": 4, "high": 6}
#     chunk_goal = goal_per_10min.get(mode, 4)

#     for path_in in tqdm(df['Path_aiff'], desc='🎧 Splitting AIFFs'):
#         y, sr = librosa.load(path_in, sr=None)
#         dur_sec = librosa.get_duration(y=y, sr=sr)

#         if dur_sec <= 300:
#             chunk_paths.append(path_in)
#             continue

#         # Set max_chunks smartly
#         est_chunks = int((dur_sec / 600) * chunk_goal)
#         max_chunks = min(10, max(est_chunks, 2))  # Always ≥2

#         # Get silence-based split points
#         intervals = librosa.effects.split(y, top_db=25)
#         boundaries = []

#         for start, end in intervals:
#             if end - start >= int(2 * sr):  # At least 2 seconds
#                 boundaries.append((start, end))

#         # If no boundaries found, fallback to force splits
#         if not boundaries:
#             total_samples = len(y)
#             chunk_len = int(len(y) / max_chunks)
#             for i in range(max_chunks):
#                 start = i * chunk_len
#                 end = (i+1) * chunk_len if i < max_chunks - 1 else total_samples
#                 boundaries.append((start, end))
#         else:
#             # Fill gaps between intervals to cover the entire file
#             full_bounds = []
#             last_end = 0
#             for start, end in boundaries:
#                 if start > last_end:
#                     full_bounds.append((last_end, start))
#                 full_bounds.append((start, end))
#                 last_end = end
#             if last_end < len(y):
#                 full_bounds.append((last_end, len(y)))
#             boundaries = full_bounds

#         # Regroup boundaries into chunks
#         chunks = []
#         current_chunk = []
#         current_len = 0
#         for start, end in boundaries:
#             seg = y[start:end]
#             seg_len = end - start
#             current_chunk.append(seg)
#             current_len += seg_len

#             if current_len >= int(2 * 60 * sr) or len(chunks) == max_chunks - 1:
#                 chunks.append(np.concatenate(current_chunk))
#                 current_chunk = []
#                 current_len = 0

#         if current_chunk:
#             chunks.append(np.concatenate(current_chunk))

#         # Slice down long chunks if any still > 5 min
#         final_chunks = []
#         for ch in chunks:
#             if len(ch) > int(5 * 60 * sr):
#                 n = int(np.ceil(len(ch) / (5 * 60 * sr)))
#                 split_len = int(len(ch) / n)
#                 for i in range(n):
#                     final_chunks.append(ch[i*split_len:(i+1)*split_len])
#             else:
#                 final_chunks.append(ch)
#         ##### important if there is a low cap of chunk
#         final_chunks = [ch for ch in final_chunks if len(ch) >= sr * 60]

#         # Cap total number of chunks to 10
#         final_chunks = final_chunks[:10]

#         # Metadata copy
#         id3_data = None
#         try:
#             id3_data = ID3(path_in)
#         except ID3NoHeaderError:
#             pass

#         # Export
#         base = os.path.splitext(os.path.basename(path_in))[0]
#         folder = os.path.dirname(path_in)

#         for i, ch in enumerate(final_chunks):
#             out_path = os.path.join(folder, f"{base}__chopNO{i+1}.aiff")
#             sf.write(out_path, ch, sr, subtype='PCM_16')
#             if id3_data:
#                 try:
#                     new_file = AIFF(out_path)
#                     new_file.tags = id3_data
#                     new_file.save()
#                 except:
#                     pass
#             chunk_paths.append(out_path)

#         # 🗑️ Delete original
#         os.remove(path_in)

#     return pd.DataFrame({'Path': chunk_paths})


# ----------------------------######----------------------------#
#   _aiff_1310_lowvolsplit_GET_chunks_df                       #
# ----------------------------######----------------------------#

import os
import numpy as np
import librosa
import soundfile as sf
from mutagen.aiff import AIFF
from mutagen.id3 import ID3, ID3NoHeaderError
import pandas as pd
from tqdm import tqdm

def _aiff_1310_lowvolsplit_GET_chunks_df(df):
    chunk_paths = []

    for path_in in tqdm(df['Path_aiff'], desc='🔍 Low-Vol Split 1–2min'):
        y, sr = librosa.load(path_in, sr=None, mono=True)
        dur_sec = librosa.get_duration(y=y, sr=sr)

        if dur_sec <= 60:
            chunk_paths.append(path_in)
            continue

        # Parameters
        min_len = 60  # seconds
        max_len = 120
        step = int(sr * 10)  # move in 10s blocks
        window = int(sr * 2)  # dip-check within ±2 sec
        quiet_cut_margin = 0.9  # percentile cutoff for silence

        rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]
        rms = librosa.util.normalize(rms)

        time_cursor = 0
        cuts = [0]

        while time_cursor + min_len * sr < len(y):
            chunk_start = time_cursor
            chunk_end = min(time_cursor + max_len * sr, len(y))

            # Search window for quietest RMS point between min-max length
            min_sample = chunk_start + int(min_len * sr)
            max_sample = int(chunk_end)

            if max_sample <= min_sample:
                break

            search_rms = rms[int(min_sample / 512):int(max_sample / 512)]
            if len(search_rms) == 0:
                break

            # Find lowest RMS point
            min_idx = np.argmin(search_rms)
            cut_sample = int(min_sample + min_idx * 512)

            # Only accept cut if it's in bottom X% volume
            if search_rms[min_idx] <= np.percentile(rms, quiet_cut_margin * 100):
                cuts.append(cut_sample)
                time_cursor = cut_sample
            else:
                # No acceptable low point found, extend time cursor to retry
                time_cursor += int(sr * 10)

        cuts.append(len(y))

        # Build chunks
        segments = []
        for i in range(len(cuts)-1):
            start = cuts[i]
            end = cuts[i+1]
            seg = y[start:end]
            if (end - start) >= min_len * sr and (end - start) <= max_len * sr:
                segments.append(seg)

        # Metadata
        id3_data = None
        try:
            id3_data = ID3(path_in)
        except ID3NoHeaderError:
            pass

        base = os.path.splitext(os.path.basename(path_in))[0]
        folder = os.path.dirname(path_in)

        for i, ch in enumerate(segments):
            out_path = os.path.join(folder, f"{base}__chopNO{i+1}.aiff")
            sf.write(out_path, ch, sr, subtype='PCM_16')
            if id3_data:
                try:
                    new_file = AIFF(out_path)
                    new_file.tags = id3_data
                    new_file.save()
                except:
                    pass
            chunk_paths.append(out_path)

        # Delete original
        os.remove(path_in)

    return pd.DataFrame({'Path': chunk_paths})


############# get BEAT samples CAI 3
def _bpm_1407_i2_GET_dominantbpm_durmin_smart(df):
    tqdm.pandas(desc="🌊 Processing Tracks")

    def analyze_bpm(file_path):
        try:
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"Missing: {file_path}")
            
            y, sr = librosa.load(file_path, sr=None)
            duration_sec = len(y) / sr
            dur_min = round(float(duration_sec / 60), 2)

            # Step 1: Try full BPM
            full_bpm, _ = librosa.beat.beat_track(y=y, sr=sr)
            if full_bpm > 30:
                full_bpm = float(full_bpm)
                return {
                    'dominant_bpm': round(full_bpm, 1),
                    'mean_bpm': round(full_bpm, 1),
                    'std_bpm': 0.0,
                    'min_bpm': round(full_bpm, 1),
                    'max_bpm': round(full_bpm, 1),
                    'variation_percentage': 0.0,
                    'bpm_consistency': 1.0,
                    'dur_min': dur_min
                }

            # Step 2: Windowed fallback
            bpm_values = []
            window_sec = 10.0
            hop_sec = 5.0

            if duration_sec < window_sec:
                raise ValueError("Too short for windowed BPM")

            exclude_start = int(0.1 * duration_sec * sr)
            exclude_end = int(0.9 * duration_sec * sr)
            y_trimmed = y[exclude_start:exclude_end]

            hop = int(hop_sec * sr)
            win = int(window_sec * sr)

            for i in range(0, len(y_trimmed) - win + 1, hop):
                window = y_trimmed[i:i+win]
                tempo, _ = librosa.beat.beat_track(y=window, sr=sr)
                if tempo > 30:
                    bpm_values.append(float(tempo))

            if not bpm_values:
                raise ValueError("No valid BPMs")

            bpm_array = np.array(bpm_values)
            dom_bpm = round(float(mode(bpm_array, keepdims=True)[0][0]), 1)
            mean_bpm = round(float(np.mean(bpm_array)), 1)
            std_bpm = round(float(np.std(bpm_array)), 1)
            min_bpm = round(float(np.min(bpm_array)), 1)
            max_bpm = round(float(np.max(bpm_array)), 1)
            variation = round(100 * std_bpm / mean_bpm, 1) if mean_bpm > 0 else 0.0
            consistency = round(1 - (std_bpm / max_bpm), 2) if max_bpm > 0 else 0.0

            return {
                'dominant_bpm': dom_bpm,
                'mean_bpm': mean_bpm,
                'std_bpm': std_bpm,
                'min_bpm': min_bpm,
                'max_bpm': max_bpm,
                'variation_percentage': variation,
                'bpm_consistency': consistency,
                'dur_min': dur_min
            }

        except Exception as e:
            warnings.warn(f"⚠️ {os.path.basename(file_path)} failed: {e}")
            return {
                'dominant_bpm': 0.0,
                'mean_bpm': 0.0,
                'std_bpm': 0.0,
                'min_bpm': 0.0,
                'max_bpm': 0.0,
                'variation_percentage': 0.0,
                'bpm_consistency': 0.0,
                'dur_min': 0.0
            }

    results = df['Path'].progress_apply(analyze_bpm)
    bpm_df = pd.DataFrame(list(results))
    return pd.concat([df.reset_index(drop=True), bpm_df], axis=1)
