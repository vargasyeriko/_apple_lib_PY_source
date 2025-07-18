# -----######-----######-----######-----######-----
# _id3_1804_i1_GET_write_year_only
# -----######-----######-----######-----######-----

from mutagen.id3 import ID3, TDRC, ID3NoHeaderError
import os
import pandas as pd
from tqdm import tqdm

def _id3_1804_i1_GET_write_year_only(df):
    """
    Writes YEAR (TDRC) tag to MP3 files using df['Path'] and df['rel_year'].
    Adds column 'year_written_id3' with result status: True / Skipped / Error.
    """

    results = []
    print("TQM: Writing YEAR tag to MP3 files...\n")

    for _, row in tqdm(df.iterrows(), total=len(df)):
        path = row.get('Path')
        rel_year = row.get('rel_year')
        status = "Skipped"

        try:
            if not os.path.isfile(path) or pd.isna(rel_year):
                status = "Skipped"
            else:
                ext = os.path.splitext(path)[1].lower()

                if ext == '.mp3':
                    try:
                        audio = ID3(path)
                    except ID3NoHeaderError:
                        audio = ID3()

                    audio.delall("TDRC")  # Optional: Clean existing date
                    audio.add(TDRC(encoding=3, text=str(rel_year)))
                    audio.save(path)
                    status = True
                else:
                    status = "Unsupported"

        except Exception as e:
            status = f"Error: {str(e)}"

        results.append(status)

    df['year_written_id3'] = results
    return df


# Classify remixer type into one of: O, R, E, U
def _remixcode_1804_i1_GET_code_remixtype(remix_col):
    """
    Input: Series with remix descriptors
    Output: Series with 1-char code: O (Original), R (Remix), E (Edit/Extended), U (Other)
    """
    def classify(entry):
        s = str(entry).lower()
        if "original" in s:
            return 'O'
        elif "remix" in s:
            return 'R'
        elif "edit" in s or "extended" in s or "rework" in s:
            return 'E'
        else:
            return 'U'

    return remix_col.apply(classify)

# -----######-----######-----######-----######-----
# FUNCTION: Extract 'bought_year' from file path
# -----######-----######-----######-----######-----

def _path_1804_i1_GET_col_bought_year(df):
    """
    Adds a column 'bought_year' by extracting the year from the folder following '_1_NEW_SOURCE' in 'Path'.

    Parameters:
        df (pd.DataFrame): Must include 'Path' column with full file paths.

    Returns:
        df (pd.DataFrame): Modified DataFrame with new column 'bought_year'.
    """
    def extract_bought_year(p):
        try:
            parts = p.split('/')
            idx = parts.index('_1_NEW_SOURCE') + 1
            folder = parts[idx]  # e.g., '_2023_this'
            return folder.split('_')[1]  # e.g., '2023'
        except Exception:
            return None

    tqdm.pandas(desc="TQM: Extracting bought_year")
    df['bought_year'] = df['Path'].progress_apply(extract_bought_year)
    return df


    