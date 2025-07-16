# ---------------------######---------------------######---------------------
#                  _convert_1010_aiff2mp3mono_GET_clean_folder
# ---------------------######---------------------######---------------------

from pydub import AudioSegment
from mutagen.aiff import AIFF
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
import os
from tqdm import tqdm

def _convert_1010_aiff2mp3mono_GET_clean_folder(folder_path):
    files = [f for f in os.listdir(folder_path) if f.lower().endswith('.aiff')]
    converted = 0
    skipped = 0

    for filename in tqdm(files, desc="🔄 Converting AIFF to MP3", unit="file"):
        full_path = os.path.join(folder_path, filename)
        base_name = os.path.splitext(filename)[0]
        mp3_path = os.path.join(folder_path, base_name + '.mp3')

        try:
            # 1. Load and convert to mono
            audio = AudioSegment.from_file(full_path, format="aiff").set_channels(1)
            audio.export(mp3_path, format="mp3", bitrate="128k")

            # 2. Copy metadata and artwork
            aiff_meta = AIFF(full_path)
            mp3_file = MP3(mp3_path, ID3=ID3)

            try:
                mp3_file.add_tags()
            except error:
                pass  # already has tags

            if aiff_meta.tags:
                for tag in aiff_meta.tags.keys():
                    try:
                        mp3_file.tags[tag] = aiff_meta.tags[tag]
                    except Exception:
                        continue

            # Copy artwork if present
            if 'APIC:' in aiff_meta.tags:
                apic = aiff_meta.tags['APIC:']
                mp3_file.tags['APIC'] = APIC(
                    encoding=3,
                    mime=apic.mime,
                    type=3,
                    desc='Cover',
                    data=apic.data
                )

            mp3_file.save()

            # 3. Remove original AIFF
            os.remove(full_path)
            converted += 1

        except Exception as e:
            print(f"⚠️ Error processing {filename}: {e}")
            skipped += 1

    print(f"\n✅ Completed: {converted} converted, {skipped} skipped.")

import os
import pandas as pd

# Define the root folder
folder_path = folder_input

# Get all full file paths recursively
file_paths = []
for root, dirs, files in os.walk(folder_path):
    for file in files:
        full_path = os.path.join(root, file)
        file_paths.append(full_path)

# Create DataFrame
df = pd.DataFrame(file_paths, columns=['Path'])
df

# ----------------------------######----------------------------#
#       _meta_1110_bpm_dur_GET_dominantbpm_and_durmin         #
# ----------------------------######----------------------------#

# ----------------------------######----------------------------#
#       _meta_1110_bpm_dur_GET_dominantbpm_and_durmin         #
# ----------------------------######----------------------------#

import os
import re
import pandas as pd
from tqdm import tqdm

def _meta_1110_bpm_dur_GET_dominantbpm_and_durmin(df):
    tqdm.pandas(desc="🌊 Extracting BPM & Duration")

    # Filter out system files
    df = df[~df['Path'].str.contains(r'/\.(DS|_).*', regex=True)].copy()

    def extract_from_path(path):
        base = os.path.splitext(os.path.basename(path))[0]

        bpm_match = re.search(r'(\d{3})-lu.', base)
        bpm = int(bpm_match.group(1)) if bpm_match else None

        sec_match = re.search(r'sec(\d+)', base)
        dur_min = round(int(sec_match.group(1)) / 60, 2) if sec_match else None

        return pd.Series([bpm, dur_min])

    df[['dominant_bpm', 'dur_min']] = df['Path'].progress_apply(extract_from_path)
    return df


###### chop phase 2


# ----------------------------######----------------------------#
#                _slice_1110_bars_GET_clean_chunks             #
# ----------------------------######----------------------------#

import os
import librosa
import numpy as np
import pandas as pd
from tqdm import tqdm

valid_exts = ['.aiff', '.wav', '.mp3']

# ----------------------------######----------------------------#
def _get_bar_duration_seconds(bpm, bars):
    return (60 / bpm) * 4 * bars

# ----------------------------######----------------------------#
def _is_chunk_loud_enough(y_chunk, threshold_db=-40):
    rms = np.sqrt(np.mean(y_chunk ** 2))
    if rms == 0:
        return False
    db = 20 * np.log10(rms)
    return db > threshold_db

# ----------------------------######----------------------------#
def _write_chunk(y, sr, out_path_mp3):
    import soundfile as sf
    import subprocess
    from mutagen.aiff import AIFF
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, error

    base_folder = os.path.dirname(out_path_mp3)
    short_base = os.path.basename(out_path_mp3)[:30]
    temp_wav = os.path.join(base_folder, f"temp_{short_base}.wav")

    os.makedirs(base_folder, exist_ok=True)

    # Mono and float32
    if len(y.shape) > 1:
        y = np.mean(y, axis=0)
    y = y.astype(np.float32)

    sf.write(temp_wav, y, sr)

    # MP3 conversion
    out_path_mp3 = out_path_mp3.replace('.wav', '.mp3')
    cmd = [
        "ffmpeg", "-y",
        "-i", temp_wav,
        "-ac", "1",
        "-ar", str(sr),
        "-b:a", "128k",
        out_path_mp3
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Copy tags from matching AIFF
    try:
        folder = os.path.dirname(out_path_mp3)
        base = os.path.basename(out_path_mp3).split("_", 1)[-1].replace('.mp3', '')
        match = [f for f in os.listdir(folder) if f.lower().endswith('.aiff') and base in f]
        if match:
            original = os.path.join(folder, match[0])
            aiff_meta = AIFF(original)
            mp3_file = MP3(out_path_mp3, ID3=ID3)
            try:
                mp3_file.add_tags()
            except error:
                pass
            if aiff_meta.tags:
                for tag in aiff_meta.tags.keys():
                    try:
                        mp3_file.tags[tag] = aiff_meta.tags[tag]
                    except Exception:
                        continue
            mp3_file.save()
    except Exception as e:
        print(f"⚠️ Metadata copy failed: {e}")

    os.remove(temp_wav)

# ----------------------------######----------------------------#
def _slice_1110_bars_GET_clean_chunks(df, rms_thresh=-40, bar_weights=None):
    if bar_weights is None:
        bar_weights = {1:6, 2:5, 4:4, 8:3, 12:2, 16:1, 32:1}

    import random
    print("\n🔁 TQM: Starting Sample Chopping...\n")

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="🌊 Processing Tracks"):
        file_path = row['Path']

        # Skip non-audio files
        if not any(file_path.lower().endswith(ext) for ext in valid_exts):
            continue

        bpm = row['dominant_bpm']
        duration_sec = row['dur_min'] * 60
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        out_folder = os.path.join(os.path.dirname(file_path), base_name)

        try:
            y, sr = librosa.load(file_path, sr=None, mono=True)
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
            continue

        duration_audio = len(y) / sr

        for bars, weight in bar_weights.items():
            bar_len_sec = _get_bar_duration_seconds(bpm, bars)
            chunk_samples = int(bar_len_sec * sr)

            if duration_audio < bar_len_sec:
                continue

            max_possible = int(duration_audio // bar_len_sec)
            chunks_to_take = min(weight, max_possible)

            valid_chunks = []
            for attempt in range(max_possible * 2):
                start_sec = random.uniform(0, duration_audio - bar_len_sec)
                start = int(start_sec * sr)
                end = start + chunk_samples
                y_chunk = y[start:end]

                if len(y_chunk) < chunk_samples:
                    continue

                if _is_chunk_loud_enough(y_chunk, threshold_db=rms_thresh):
                    valid_chunks.append((start, end, start_sec))

                if len(valid_chunks) >= chunks_to_take:
                    break

            for i, (start, end, _) in enumerate(valid_chunks[:chunks_to_take]):
                y_chunk = y[start:end]
                if bars <= 8:
                    suffix = f"_s{bars}{i+1}_"
                elif bars == 12:
                    suffix = f"_sa{i+1}_"
                elif bars == 16:
                    suffix = f"_sb{i+1}_"
                elif bars == 32:
                    suffix = f"_sc{i+1}_"
                else:
                    suffix = f"_x{i+1}_"

                out_name = f"{suffix}{base_name}.mp3"
                out_path = os.path.join(out_folder, out_name)
                _write_chunk(y_chunk, sr, out_path)

    print("\n✅ TQM: All samples processed and saved.\n")




# ----------------------------######----------------------------#
#      _id3_1010_coverembed_GET_df_folder_updatedfiles         #
# ----------------------------######----------------------------#

import os
import pandas as pd
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
from tqdm import tqdm

def _id3_1010_coverembed_GET_df_folder_updatedfiles(df):
    updated_log = []

    for file_path in tqdm(df["Path"], desc="🔁 Processing all source MP3s"):
        if not os.path.isfile(file_path) or not file_path.lower().endswith(".mp3"):
            continue

        folder_path = file_path.replace(".mp3", "")
        if not os.path.isdir(folder_path):
            print(f"❌ Folder not found: {folder_path}")
            continue

        try:
            id3 = ID3(file_path)
            apic_tags = [tag for tag in id3.values() if isinstance(tag, APIC)]
            if not apic_tags:
                print(f"⚠️ No cover in: {file_path}")
                continue
            cover_data = apic_tags[0].data
            mime = apic_tags[0].mime
        except error as e:
            print(f"❌ ID3 Error in source MP3: {file_path} — {e}")
            continue

        mp3_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".mp3")]

        for mp3_file in mp3_files:
            full_path = os.path.join(folder_path, mp3_file)
            try:
                audio = MP3(full_path, ID3=ID3)
                if audio.tags is None:
                    audio.add_tags()
                audio.tags.delall("APIC")
                audio.tags.add(
                    APIC(
                        encoding=3,
                        mime=mime,
                        type=3,
                        desc="Cover",
                        data=cover_data
                    )
                )
                audio.save()
                updated_log.append(full_path)
            except Exception as e:
                print(f"⚠️ Failed to embed for {full_path}: {e}")

    print(f"\n✅ Embedded cover to {len(updated_log)} MP3s total.")
    return updated_log


# ----------------------------######----------------------------#
#       _key_1110_mp3folders_GET_3topkeys_dj_and_music         #
# ----------------------------######----------------------------#

import os
import librosa
import numpy as np
import pandas as pd
from tqdm import tqdm

tqdm.pandas()

# Normalize key strings
def normalize_key(key_str):
    key_str = key_str.lower().replace('-', '').replace(' ', '')
    key_str = key_str.replace('flat', 'b').replace('sharp', '#')
    return key_str

# Camelot to music mapping
camelot_to_key = {
    "1A": ["G#min","A-Flat Minor","Ab Minor","G-sharp minor","G# minor"],
    "1B": ["Bmaj", "B Major"],
    "2A": ['D#min',"E-Flat Minor","Eb Minor","D-sharp minor","D# minor"],
    "2B": ["F#maj","F# Major", "F-Sharp Major","G Flat major","Gb major"],
    "3A": ["A#min","B-Flat Minor","Bb Minor","A-Sharp minor" ,"A# minor"],
    "3B": ["C#maj","D-Flat Major","Db Major","C-sharp major","C# major"],
    "4A": ["Fmin","F Minor"],
    "4B": ["G#maj","A-Flat Major", "Ab Major","G Sharp major","G# major"],
    "5A": ["Cmin","C Minor"],
    "5B": ["D#maj","E-Flat Major","Eb Major"],
    "6A": ["Gmin","G Minor",'G_Minor'],
    "6B": ["A#maj", "B-Flat Major","Bb Major","A Sharp major","A# major"],
    "7A": ["Dmin" , "D Minor"],
    "7B": ["Fmaj", "F Major"],
    "8A": ["Amin","A Minor"],
    "8B": ["Cmaj","C Major"],
    "9A": ["Emin" , "E Minor" ],
    "9B": ["Gmaj" , "G Major"],
    "10A":["Bmin" , "B Minor" ],
    "10B":["Dmaj", "D Major" ],
    "11A": ["F#min","F# Minor", "F-Sharp Minor","G Flat minor","Gb minor"],
    "11B": ["Amaj", "A Major"],
    "12A": ['C#min',"D-Flat Minor","Db Minor","D B Minor","C Sharp minor","C# minor"],
    "12B": ["Emaj", "E Major"]
}

music_to_camelot = {}
for dj_key, variants in camelot_to_key.items():
    for mkey in variants:
        norm = normalize_key(mkey)
        if norm not in music_to_camelot:
            music_to_camelot[norm] = dj_key

# Detect 3 most prominent keys
def detect_top3_keys(audio_path, sr=22050):
    try:
        y, _ = librosa.load(audio_path, sr=sr, mono=True)
    except Exception as e:
        return [np.nan, np.nan, np.nan]
    
    total_samples = len(y)
    y_middle = y[int(0.15*total_samples):int(0.85*total_samples)]
    y_harmonic = librosa.effects.harmonic(y_middle)
    chroma = librosa.feature.chroma_cqt(y=y_harmonic, sr=sr)
    
    chroma_avg = np.mean(chroma, axis=1)
    if np.sum(chroma_avg) == 0:
        return [np.nan, np.nan, np.nan]
    
    chroma_norm = chroma_avg / np.sum(chroma_avg)
    
    major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
    major_profile /= np.sum(major_profile)
    minor_profile /= np.sum(minor_profile)
    
    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    results = []
    for i in range(12):
        r_maj = np.roll(major_profile, i)
        r_min = np.roll(minor_profile, i)
        cmaj = np.corrcoef(r_maj, chroma_norm)[0, 1]
        cmin = np.corrcoef(r_min, chroma_norm)[0, 1]
        results.append((cmaj, f"{keys[i]}maj"))
        results.append((cmin, f"{keys[i]}min"))
    
    top3 = sorted(results, key=lambda x: x[0], reverse=True)[:3]
    return [k[1] for k in top3]

# Convert to DJ keys
def map_3_keys(row):
    mapped = []
    for key in [row['KEY_1'], row['KEY_2'], row['KEY_3']]:
        norm = normalize_key(key) if isinstance(key, str) else None
        dj_key = music_to_camelot.get(norm, np.nan)
        mapped.append(dj_key)
    return pd.Series(mapped, index=['key_dj_1', 'key_dj_2', 'key_dj_3'])

# MAIN FUNCTION
def _key_1110_mp3folders_GET_3topkeys_dj_and_music(folder_list, sr=22050):
    paths = []
    for base in folder_list:
        for root, _, files in os.walk(base):
            for f in files:
                if f.lower().endswith(".mp3") and not f.startswith("._"):
                    paths.append(os.path.join(root, f))
    
    df = pd.DataFrame(paths, columns=['Path'])
    df[['KEY_1', 'KEY_2', 'KEY_3']] = df['Path'].progress_apply(lambda x: pd.Series(detect_top3_keys(x, sr)))
    df[['key_dj_1', 'key_dj_2', 'key_dj_3']] = df.progress_apply(map_3_keys, axis=1)
    
    return df


# atn get folder list 
# get folder names 

# ----------------------------######----------------------------#
#        _list_1107_foldersonly_GET_fullpaths_recursively      #
# ----------------------------######----------------------------#

import os

def _list_1107_foldersonly_GET_fullpaths_recursively(root_folder):
    """
    Return a list of full folder paths (recursively) starting from root_folder.
    Only directories are included in the output.
    """
    folder_paths = []

    for dirpath, dirnames, _ in os.walk(root_folder):
        for folder in dirnames:
            full_path = os.path.join(dirpath, folder)
            folder_paths.append(full_path)

    return folder_paths

# ----------------------------######----------------------------#
#    _key_1110_dfkeys_RENAME_by_top3keys_and_clean_filename    #
# ----------------------------######----------------------------#

import os
import re
import pandas as pd

def _key_1110_dfkeys_RENAME_by_top3keys_and_clean_filename(df_keys):
    """
    Cleans and renames MP3 files by:
    - Removing: ---###-VARIOUS-######vocalssil### and ---sec###
    - Retaining the 'luX' marker after the base name
    - Inserting the 3 most prominent keys after 'luX'
    - Moving BPM to the end, as --###.mp3
    """

    row = df_keys.iloc[0]
    original = os.path.basename(row['Path'])

    # Clean filename
    cleaned = re.sub(r'---\d+-VARIOUS-\d+vocalssil\d+', '', original)
    cleaned = re.sub(r'---sec\d+', '', cleaned)

    # Extract keys
    key_str = f"{row['key_dj_3']}-{row['KEY_3']}-{row['key_dj_2']}-{row['KEY_2']}_{row['key_dj_1']}-{row['KEY_1']}"

    # Match pattern: BPM-luX (any 3-digit BPM + luM/luK/luQ/etc.)
    match = re.search(r'-(\d+)-(lu\w)\.mp3$', cleaned)
    if match:
        bpm = match.group(1)
        lux = match.group(2)
        prefix = cleaned[:match.start()]
        renamed = f"{prefix}-{lux}-{key_str}-{bpm}.mp3"
    else:
        renamed = cleaned.replace('.mp3', f"-{key_str}.mp3")

    print("\n🔁 Example:")
    print(f"Original: {original}")
    print(f"Renamed : {renamed}\n")

    #input("⚠️  Press ENTER to rename ALL files, or CTRL+C to cancel.\n")

    # === BULK LOOP ===
    for i, row in df_keys.iterrows():
        try:
            old_path = row['Path']
            folder = os.path.dirname(old_path)
            filename = os.path.basename(old_path)

            # Clean filename
            base = re.sub(r'---\d+-VARIOUS-\d+vocalssil\d+', '', filename)
            base = re.sub(r'---sec\d+', '', base)

            # Key string
            key_str = f"{row['key_dj_3']}-{row['KEY_3']}-{row['key_dj_2']}-{row['KEY_2']}_{row['key_dj_1']}-{row['KEY_1']}"

            match = re.search(r'-(\d+)-(lu\w)\.mp3$', base)
            if match:
                bpm = match.group(1)
                lux = match.group(2)
                prefix = base[:match.start()]
                new_name = f"{prefix}-{lux}-{key_str}-{bpm}.mp3"
            else:
                new_name = base.replace('.mp3', f"-{key_str}.mp3")

            new_path = os.path.join(folder, new_name)
            os.rename(old_path, new_path)
            df_keys.at[i, 'Path'] = new_path

        except Exception as e:
            print(f"❌ Rename failed for {filename}: {e}")

    print("\n✅ All files successfully renamed.")
    return df_keys

######### # -----######-----###### QUICK EXT TO MP3 -----######-----###### #
import os
def _path_1607_i2_GET_mp3(df):
    from tqdm import tqdm; tqdm.pandas(desc="🔁 .mp3 EXT")
    df['Path_mp3'] = df['Path'].progress_apply(lambda x: os.path.splitext(x)[0] + '.mp3' if isinstance(x, str) else x)
    return df


