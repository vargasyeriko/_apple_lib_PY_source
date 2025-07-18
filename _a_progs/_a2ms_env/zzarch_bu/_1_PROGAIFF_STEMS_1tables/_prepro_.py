# 0_FNS ────────────────────────────────────────────────────────────────────────
# -----######-----######  AIFF CONVERTER v6  (_NNNN_ prefix)  -----######-----######
from pathlib import Path
from collections import Counter
from subprocess import run, PIPE, CalledProcessError
from tqdm import tqdm

audio_extensions = [
    "aiff", "aif", "wav", "flac", "alac", "mp3", "m4a", "aac", "ogg", "wma"
]

def _aiff_2904_i6_GET_numbered_all(
    root_dir,
    out_dir,
    target_sr=44100,
    target_bit=16,
    target_ch=2,
    overwrite=False,
    show_err=True
):
    root_dir, out_dir = Path(root_dir).expanduser(), Path(out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    exts = {e.lower().lstrip(".") for e in audio_extensions}
    codec = f"pcm_s{target_bit}be"
    static_args = ["-ar", str(target_sr), "-ac", str(target_ch), "-c:a", codec]

    paths = [p for p in root_dir.rglob("*")
             if p.is_file() and p.suffix.lower().lstrip(".") in exts
             and not p.name.startswith(("._", ".DS"))]

    total = len(paths)
    width = len(str(total)) if total > 0 else 3
    freq = Counter()

    tqm = tqdm(enumerate(paths, 1), total=total, desc="TQM: transcoding ➜ AIFF")
    for idx, src in tqm:
        prefix = src.relative_to(root_dir).parts[0] if len(src.parts) > 1 else "ROOT"
        id_tag = f"_{idx:0{width}d}_"
        dst = out_dir / f"{id_tag}{prefix}_{src.stem}.aiff"

        if dst.exists() and not overwrite:
            continue

        cmd = ["ffmpeg", "-y" if overwrite else "-n", "-i", str(src), *static_args, str(dst)]
        try:
            run(cmd, stdout=PIPE, stderr=PIPE, check=True)
            freq[src.suffix.lower().lstrip(".")] += 1
        except CalledProcessError as e:
            if show_err:
                err = e.stderr.decode(errors="ignore").splitlines()[:8]
                tqdm.write(f"❌ FFmpeg on {src}:\n    " + "\n    ".join(err))
            else:
                tqdm.write(f"❌ FFmpeg failed on: {src}")

    tqdm.write(f"✅ Done — {sum(freq.values()):,} files converted")
    return freq
# -----######-----######  END MAIN FUNCTION  -----######-----######

# !#!#!#!#! RUNNING STATEMENTS !#!#!#!#!
# -----######-----###### RENAME FINAL: TITLE ONLY VARIANTS -----######-----######
import os
import pandas as pd
from tqdm import tqdm
from datetime import datetime

def _rename_0605_titleonly_GET_renamed_folder_files(
    aiff_dir,
    custom_artist="YODJ",
    custom_genre="Genre",
    custom_label="Label",
    custom_release_date="2025_01_01",
    custom_purchase_date=""
):
    """
    Rename AIFF files using their filename as title + custom tag structure.

    Args:
        aiff_dir (str): Path to folder containing AIFF files
        custom_artist (str): Custom artist tag (max 25 characters)
        custom_genre (str): Custom genre tag
        custom_label (str): Custom label tag
        custom_release_date (str): YYYY_MM_DD format
        custom_purchase_date (str): YYYY_MM_DD format or empty for today

    Returns:
        pd.DataFrame: DataFrame with original and renamed paths
    """
    tqdm.pandas()
    files = [f for f in os.listdir(aiff_dir) if f.lower().endswith('.aiff')]
    data = []

    def clean(s):
        return (
            str(s)
            .replace(" ", "_").replace("/", "___").replace(",", "_")
            .replace("(", "").replace(")", "").replace("!", "")
            .replace("&", "and").replace("’", "").replace("'", "")
            .replace("¿", "").replace("¡", "").replace(":", "")
            .replace(";", "").strip()
        )

    for f in tqdm(files, desc="Renaming files"):
        original_path = os.path.join(aiff_dir, f)
        title = clean(os.path.splitext(f)[0])[:25]

        remix = "original" if "mix" not in title.lower() and "remix" not in title.lower() else title
        artist_val = clean(custom_artist)[:25]
        genre_val = clean(custom_genre)
        label_val = clean(custom_label)
        key = "NA"
        bpm = "NA"
        ext = ".aiff"
        release_val = custom_release_date
        purchase_val = (
            custom_purchase_date if custom_purchase_date else datetime.today().strftime('%Y_%m_%d')
        )

        new_name = (
            f"TRkw_{title}_ARkw_{artist_val}_MXkw_{remix}_KYkw_{key}_"
            f"BPkw_{bpm}_GNkw_{genre_val}_LBkw_{label_val}_RYkw_{release_val}_"
            f"PYkw_{purchase_val}{ext}"
        )

        if len(new_name) > 240:
            new_name = new_name[:230] + ext

        new_path = os.path.join(aiff_dir, new_name)

        try:
            os.rename(original_path, new_path)
            data.append({"Original": original_path, "Renamed": new_path})
        except Exception as e:
            print(f"❌ Failed to rename: {original_path} -> {e}")
            data.append({"Original": original_path, "Renamed": None})

    return pd.DataFrame(data)

# -----######-----###### DELUXE AIFF NORMALIZER (NO CLIP) -----######-----######
import os
import numpy as np
import soundfile as sf
from tqdm import tqdm

def _audio_0605_deluxenorm_GET_overwrite_noclip_aiffs(aiff_dir):
    """
    Normalize AIFF files in a folder to -0.1 dBFS safely.
    Skips silent or already-normalized files.
    
    Args:
        aiff_dir (str): Directory containing AIFF files to normalize.
    """
    if not os.path.isdir(aiff_dir):
        raise NotADirectoryError(f"❌ Folder does not exist: {aiff_dir}")

    aiff_files = [f for f in os.listdir(aiff_dir) if f.lower().endswith(".aiff") and not f.startswith("._")]
    print(f"🎧 Found {len(aiff_files)} AIFF files. Starting deluxe normalization...\n")

    for fname in tqdm(aiff_files, desc="🎚️  Deluxe Normalizing"):
        full_path = os.path.join(aiff_dir, fname)
        try:
            data, sr = sf.read(full_path, dtype='float32')
            peak = np.max(np.abs(data))

            if peak == 0:
                continue  # Skip silent files

            target_peak = 10 ** (-0.1 / 20)  # ≈ 0.98855
            gain = target_peak / peak

            if 0.95 < gain < 1.05:
                continue  # Already close enough to target

            norm_data = data * gain
            if np.max(np.abs(norm_data)) >= 1.0:
                print(f"⚠️ Skipped {fname} (risk of clipping)")
                continue

            sf.write(full_path, norm_data, sr, format='AIFF')

        except Exception as e:
            print(f"❌ Error processing {fname}: {e}")
