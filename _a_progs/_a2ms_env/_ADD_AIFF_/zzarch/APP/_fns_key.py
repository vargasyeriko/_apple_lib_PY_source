# ----- TQM BAR -----
# -----######----- CORE FUNCTION: MIDDLE KEY DETECTION FOR AIFF DJ MIXING -----######-----
import os
import librosa
import numpy as np
import pandas as pd
from tqdm import tqdm

# Initialize the tqdm progress bar for pandas
tqdm.pandas()

def _key_0815_librosa_middle_aiff_GET_output(audio_file: str, sr: int = 22050) -> str:
    """
    Detects the musical key (Major/Minor) from an AIFF file using only the middle 70% portion of the track.
    
    The first 15% (intro) and the last 15% (outro) are ignored to focus on the main, "saucy" section for DJ mixing.
    This function is optimized for AIFF files and returns an error if the file is not in AIFF format.
    
    Parameters:
        audio_file (str): The path to the AIFF audio file.
        sr (int): The sample rate for processing. Defaults to 22050 Hz.
    
    Returns:
        str: The detected key in abbreviated form (e.g., "Amaj" or "Bmin") or an error message.
    """
    # Ensure the file is in AIFF format (accepting both .aiff and .aif extensions)
    if not audio_file.lower().endswith(('.aiff', '.aif')):
        return "Error: The audio file must be in AIFF format."
    
    try:
        # Load the full audio file (do not modify the original file)
        y, _ = librosa.load(audio_file, sr=sr, mono=True)
    except Exception as e:
        return f"Error loading file: {e}"
    
    # Calculate indices to retain the middle 70% of the song (dropping first and last 15%)
    total_samples = len(y)
    start_idx = int(0.15 * total_samples)
    end_idx = int(0.85 * total_samples)
    y_middle = y[start_idx:end_idx]
    
    # ----- TQM BAR -----
    # Emphasize the tonal content by extracting the harmonic component in the middle section
    y_harmonic = librosa.effects.harmonic(y_middle)
    
    # Compute chroma features using the constant-Q transform on the harmonic segment
    chroma = librosa.feature.chroma_cqt(y=y_harmonic, sr=sr)
    
    # Average the chroma features over time
    chroma_avg = np.mean(chroma, axis=1)
    if np.sum(chroma_avg) == 0:
        return "No energy detected in the main section"
    
    chroma_norm = chroma_avg / np.sum(chroma_avg)
    
    # ----- TQM: Processing KEY -----
    # Define normalized Krumhansl-Schmuckler profiles for Major and Minor keys
    major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
    major_profile = major_profile / np.sum(major_profile)
    minor_profile = minor_profile / np.sum(minor_profile)
    
    # List of pitch classes beginning at C
    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    best_correlation = -np.inf
    best_key = ''
    best_mode = ''
    
    # Rotate each key profile to align with every possible tonic and compute correlation
    for i in range(12):
        rotated_major = np.roll(major_profile, i)
        rotated_minor = np.roll(minor_profile, i)
        
        corr_major = np.corrcoef(rotated_major, chroma_norm)[0, 1]
        corr_minor = np.corrcoef(rotated_minor, chroma_norm)[0, 1]
        
        if corr_major > best_correlation:
            best_correlation = corr_major
            best_key = keys[i]
            best_mode = "Major"
        if corr_minor > best_correlation:
            best_correlation = corr_minor
            best_key = keys[i]
            best_mode = "Minor"
    
    # Return the key in abbreviated format ("maj" for Major, "min" for Minor)
    return f"{best_key}{'maj' if best_mode == 'Major' else 'min'}"

# ----- TQM BAR -----
# -----######----- CORE FUNCTION: BULK PROCESSING FOR AIFF KEY DETECTION -----######-----
def _key_bulk_0815_librosa_middle_aiff_GET_output(df: pd.DataFrame, sr: int = 22050) -> pd.DataFrame:
    """
    Processes a DataFrame in bulk by reading the audio files specified in the 'Path' column,
    detects the key from the middle 70% of each track (optimized for AIFF files), and appends
    the detected key to a new column named 'KEY_py'.
    
    The process features a progress bar to display the status of the computation.
    
    Parameters:
        df (pd.DataFrame): A DataFrame that contains at least a 'Path' column with audio file paths.
        sr (int): The sample rate for processing. Defaults to 22050 Hz.
    
    Returns:
        pd.DataFrame: The original DataFrame with an added 'KEY_py' column containing the detected keys.
    """
    # Apply the key detection function to each audio file path using a progress bar.
    df['KEY'] = df['Path'].progress_apply(lambda path: _key_0815_librosa_middle_aiff_GET_output(path, sr=sr))
    return df

############################### get key_dj and key_misic normalized same format 



# -----######-----######-----######-----######-----######-----######-----

#### KEYyY
##
#
    # 0_FNS: Core Functions and Definitions
##############################################
import numpy as np
import pandas as pd
from tqdm import tqdm
import re

# Provided Camelot dictionary (unaltered)
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
    "8B": ["Cmaj","C Major"], # done
    
    "9A": ["Emin" , "E Minor" ],
    "9B": ["Gmaj" , "G Major"],
    "10A":["Bmin" , "B Minor" ],
    "10B":["Dmaj", "D Major" ],
    
    "11A": ["F#min","F# Minor", "F-Sharp Minor","G Flat minor","Gb minor"],
    "11B": ["Amaj", "A Major"],
    "12A": ['C#min',"D-Flat Minor","Db Minor","D B Minor","C Sharp minor","C# minor"],
    "12B": ["Emaj", "E Major"]}

# ---------------------------
# Helper: Normalize musical key strings.
def normalize_key(key_str: str) -> str:
    """
    Normalize musical key strings for comparison.
    Converts to lowercase, removes hyphens and spaces, and
    substitutes 'flat' with 'b' and 'sharp' with '#'.
    """
    key_str = key_str.lower()
    key_str = key_str.replace('-', '')
    key_str = key_str.replace(' ', '')
    key_str = key_str.replace('flat', 'b')
    key_str = key_str.replace('sharp', '#')
    return key_str

# ---------------------------
# Build reverse mapping: musical key (normalized) to DJ Camelot key.
music_to_camelot = {}
for dj_key, music_list in camelot_to_key.items():
    for m_key in music_list:
        norm = normalize_key(m_key)
        if norm not in music_to_camelot:
            music_to_camelot[norm] = dj_key

# ---------------------------
# ASCII Art header for core function
##############################################
#  ###############################
#  # CORE FUNCTION: _key_0403_i2_GET_keys
#  # Converts the 'KEY' column (either DJ/Camelot or musical notation)
#  # into two columns: 'key_dj' and 'key_music'.
#  # Single-letter inputs (e.g., "A" or "B") are assumed to be majors.
#  ###############################

def _key_0403_i2_GET_keys(df: pd.DataFrame) -> pd.DataFrame:
    """
    Processes the 'KEY' column of the DataFrame and creates two new columns:
    'key_dj' (Camelot notation) and 'key_music' (standard musical key).

    - If the input value is in DJ key (e.g., '1A'), it returns that as key_dj and
      the first mapped musical key from camelot_to_key as key_music.
    - If the input is in musical notation, it normalizes the string and uses a reverse
      mapping to determine its corresponding DJ key.
    - If the value is a single letter (like 'A' or 'B'), it assumes a major key.
    - If no match is found, both columns are set to np.nan.
    """
    tqdm.pandas(desc="Processing keys")
    
    def map_key(value):
        # Handle missing or non-string values.
        if pd.isna(value) or not isinstance(value, str):
            return pd.Series([np.nan, np.nan])
        value_strip = value.strip()
        # Check if the value is in DJ (Camelot) notation (case-insensitive).
        if value_strip.upper() in camelot_to_key:
            dj_key = value_strip.upper()
            music_key = camelot_to_key[dj_key][0]  # Use the first variant as canonical.
            return pd.Series([dj_key, music_key])
        else:
            # If value is a single letter (A-G), assume it is Major.
            if re.fullmatch(r"[A-Ga-g]", value_strip):
                value_strip = value_strip.upper() + " Major"
            # Normalize and check if in reverse mapping.
            norm_value = normalize_key(value_strip)
            if norm_value in music_to_camelot:
                dj_key = music_to_camelot[norm_value]
                music_key = camelot_to_key[dj_key][0]
                return pd.Series([dj_key, music_key])
            else:
                return pd.Series([np.nan, np.nan])
    
    df[['key_dj', 'key_music']] = df['KEY'].progress_apply(map_key)
    return df

    
# -----######-----######-----###### FUNCTION -----######-----######-----######

########### write key to ID3 tags 

def _write_tags_2712_id3_SET_key_bulk(df, path_col, key_dj_col):
    """
    Overwrites the existing TKEY (musical key) ID3 tag of AIFF files with the value from the key_dj column.
    
    Parameters:
    - df: DataFrame containing file paths and key_dj values.
    - path_col: Column name in the DataFrame containing AIFF file paths.
    - key_dj_col: Column name in the DataFrame containing key_dj values.
    
    Returns:
    - DataFrame: Updated with a 'status' column indicating success or error messages.
    
    Notes:
    - This function overwrites the TKEY tag completely.
    - The new TKEY tag is written as a list of text.
    """
    import mutagen
    from mutagen.aiff import AIFF
    from mutagen.id3 import TKEY
    import os
    import pandas as pd

    results = []

    for index, row in df.iterrows():
        aiff_path = row[path_col]
        key_text = row[key_dj_col]

        # Check for missing key_dj value.
        if pd.isna(key_text) or key_text == "":
            results.append("Skipped: No key_dj value")
            continue

        # Verify that the file exists.
        if not os.path.isfile(aiff_path):
            results.append(f"Error: File not found at {aiff_path}")
            continue

        try:
            # Load the AIFF file.
            audio = AIFF(aiff_path)

            # Add ID3 tags if not already present.
            if not hasattr(audio, "tags") or audio.tags is None:
                audio.add_tags()

            # Overwrite any existing TKEY tag.
            if "TKEY" in audio.tags:
                del audio.tags["TKEY"]

            # Add new TKEY tag with key_dj value (as a list).
            audio.tags.add(TKEY(encoding=3, text=[str(key_text)]))

            # Save the changes.
            audio.save()
            results.append("Success: TKEY updated")
        except Exception as e:
            results.append(f"Error: {e}")

    # Add results to DataFrame.
    df["status"] = results
    return df


####################### get equivalents for chamelot map 