# 0_FNS
# -----######-----###### IMPORT STATEMENTS & CORE FUNCTION
from mutagen import File
from tqdm import tqdm
import pandas as pd

# Enable progress_apply for pandas
tqdm.pandas()

def _reldate_0204_id3_filefallback_GET_df_with_rel_date(df, var, btw_front, btw_back):
    """
    Extracts a complete release date from the ID3 tags of AIFF files in the dataframe.
    It first attempts to retrieve a full date from the tags ("TDRL" then "TDRC"). 
    If the tag contains only a year or an incomplete date, the value is set to None and 
    a fallback extraction from the file name is applied.

    The fallback function now supports dates with underscores (e.g. "2014_06_28") and 
    converts them to the format "YYYY-MM-DD".

    Parameters:
        df (DataFrame): DataFrame containing at least 'Path' and 'temp_id' columns.
        var (str): The column name to update with the complete release date.
        btw_front (str): The marker string indicating the start of the date in the 'temp_id' column.
        btw_back (str): The marker string indicating the end of the date in the 'temp_id' column.

    Returns:
        DataFrame: The updated DataFrame with new columns 'rel_date' (extracted complete date)
                   and 'rel_date_file' (indicating the extraction source: 'ID3TAGS' or 'FILE_NAME').
    """
    import os

    rel_dates = []
    rel_date_sources = []

    for path in tqdm(df['Path'], desc="Extracting ID3 Release Date"):
        date_from_tag = None
        try:
            audio = File(path)
            if audio and hasattr(audio, "tags") and audio.tags:
                # Try TDRL (release time) first, then fall back to TDRC (recording time)
                tag = audio.tags.get("TDRL")
                if not tag:
                    tag = audio.tags.get("TDRC")
                if tag:
                    date_tag_str = str(tag).strip()
                    # Check if the tag contains a complete date with dashes (e.g., YYYY-MM-DD)
                    if "-" in date_tag_str:
                        parts = date_tag_str.split("-")
                        if len(parts) == 3 and all(part for part in parts):
                            date_from_tag = date_tag_str
                        else:
                            date_from_tag = None
                    elif len(date_tag_str) == 8:
                        # Assume format is YYYYMMDD; reformat as YYYY-MM-DD
                        date_from_tag = date_tag_str[:4] + "-" + date_tag_str[4:6] + "-" + date_tag_str[6:]
                    else:
                        # Incomplete date (e.g., only year)
                        date_from_tag = None
        except Exception:
            date_from_tag = None

        if date_from_tag:
            rel_dates.append(date_from_tag)
            rel_date_sources.append("ID3TAGS")
        else:
            rel_dates.append(None)
            rel_date_sources.append("FILE_NAME")

    df['rel_date'] = rel_dates
    df['rel_date_file'] = rel_date_sources

    # Define fallback extraction function to get complete date from the file name.
    def _file_extract_date_from_file_name_(df, var, btw_front, btw_back):
        empty_values = [None, "", "None", "NAN", "NaN", "nan",
                        "Error: argument of type 'NoneType' is not iterable"]
        missing_date_idx = df[f'{var}'].isin(empty_values) | df[f'{var}'].isnull()

        def extract_date_from_temp_id(temp_id):
            if isinstance(temp_id, str) and btw_front in temp_id and btw_back in temp_id:
                start = temp_id.find(btw_front) + len(btw_front)
                end = temp_id.find(btw_back, start)
                extracted = temp_id[start:end].strip()
                # Check for a full date with dashes
                if "-" in extracted:
                    parts = extracted.split("-")
                    if len(parts) == 3 and all(part for part in parts):
                        return extracted
                # Check for a full date with underscores (e.g., "2014_06_28")
                elif "_" in extracted:
                    parts = extracted.split("_")
                    if len(parts) == 3 and len(parts[0])==4 and len(parts[1])==2 and len(parts[2])==2:
                        return parts[0] + "-" + parts[1] + "-" + parts[2]
                # Check for a contiguous 8-digit date (YYYYMMDD)
                elif len(extracted) == 8 and extracted.isdigit():
                    return extracted[:4] + "-" + extracted[4:6] + "-" + extracted[6:]
            return None

        # Use progress_apply for the fallback extraction
        df.loc[missing_date_idx, f'{var}'] = df.loc[missing_date_idx, 'temp_id'].progress_apply(extract_date_from_temp_id)
        return df

    # Apply fallback to rows where a complete release date wasn't found in the ID3 tags.
    df_missing = df[df['rel_date'].isnull()].copy()
    if not df_missing.empty:
        df_missing[var] = df_missing.get(var, None)
        df_fallback = _file_extract_date_from_file_name_(df_missing, var, btw_front, btw_back)
        df.loc[df_fallback.index, 'rel_date'] = df_fallback[var]

    return df

####
## NOw write the release date to the tags 
#

# -----######-----######-----######-----######-----######-----######-----

# 0_FNS
# -----######-----###### IMPORT STATEMENTS & CORE FUNCTION
# 0_FNS
# -----######-----###### IMPORT STATEMENTS & CORE FUNCTION
import os
from mutagen.aiff import AIFF
from mutagen.id3 import TDRL
from tqdm import tqdm

def _write_reldate_id3_bulk(df, path_col='Path', reldate_col='rel_date'):
    """
    Updates (or adds) the ID3 release date tag (TDRL) for AIFF files specified in the DataFrame.
    The function writes the release date exactly as stored in the DataFrame's release date column.
    Instead of deleting the existing tag, it updates the text if the tag is already present.
    
    Parameters:
        df (pandas.DataFrame): DataFrame containing:
            - 'rel_date': The release date value to be written.
            - 'Path': The file path to the corresponding AIFF file.
        path_col (str): Column name for file paths (default 'Path').
        reldate_col (str): Column name for release date values (default 'rel_date').
    
    Returns:
        int: The total number of files successfully processed.
    """
    success_count = 0

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Writing AIFF files for: release date"):
        file_path = row[path_col]
        release_date = row[reldate_col]
        
        if not os.path.isfile(file_path):
            print(f"File not found: {file_path}")
            continue

        try:
            # Load the AIFF file
            audio = AIFF(file_path)
            
            # Add ID3 tags if missing
            if not hasattr(audio, "tags") or audio.tags is None:
                audio.add_tags()
            
            # Update existing TDRL tag if present, otherwise add new one.
            if "TDRL" in audio.tags:
                audio.tags["TDRL"].text = [release_date]
            else:
                audio.tags.add(TDRL(encoding=3, text=[release_date]))
            
            # Save the updated tags back to the file (only metadata is updated)
            audio.save()
            success_count += 1
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
    
    print(f"Total files processed for release date: {success_count}")
    return success_count


# -----######-----######-----######-----######-----######-----######-----

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
    "1A": ["A-Flat Minor","Ab Minor","G-sharp minor","G# minor"],
    "1B": ["B Major"],
    "2A": ["E-Flat Minor","Eb Minor","D-sharp minor","D# minor"],
    "2B": ["F# Major", "F-Sharp Major","G Flat major","Gb major"],
    "3A": ["B-Flat Minor","Bb Minor","A-Sharp minor" ,"A# minor"],
    "3B": ["D-Flat Major","Db Major","C-sharp major","C# major"],
    "4A": ["F Minor"],
    "4B": ["A-Flat Major", "Ab Major","G Sharp major","G# major"],
    "5A": ["C Minor"],
    "5B": ["E-Flat Major","Eb Major"],
    "6A": ["G Minor",'G_Minor'],
    "6B": ["B-Flat Major","Bb Major","A Sharp major","A# major"],
    "7A": ["Dmin" , "D Minor"],
    "7B": [ "Fmaj", "F Major"],
    "8A": ["Amin","A Minor"],
    "8B": ["Cmaj","C Major"],
    "9A": ["Emin" , "E Minor" ],
    "9B": [ "Gmaj" , "G Major"],
    "10A": ["Bmin" , "B Minor" ],
    "10B": ["D Major" , "Dmaj"],
    "11A": ["F# Minor", "F-Sharp Minor","G Flat minor","Gb minor"],
    "11B": ["A Major", "Amin"],
    "12A": ["D-Flat Minor","Db Minor","D B Minor","C Sharp minor","C# minor"],
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


# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----

####
##

# -----######-----######-----###### FUNCTION -----######-----######-----######
# -----######-----######-----###### FUNCTION -----######-----######-----######
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


#

# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----

####
##
#

# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----

####
##
#

# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
####
##
#

# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----

####
##
#

# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----