import pandas as pd
import os
from tqdm import tqdm
"""This function searches the provided folder path for all specified music file extensions (case insensitive),
or, if no file extensions are provided, it will return all files regardless of extension.

Filters out unwanted files (starting with '._' and '.DS'), and returns a DataFrame containing the file path,
the base name without extension ('Name'), the full file name ('file_name'), and the size in MB.

It also includes a progress tracker (TQM) for better feedback and handles mixed case extensions.

Parameters:
- my_folder_path (str): The folder path where the search should be performed.
- file_extensions (list, optional): A list of file extensions to search for (e.g., ['.wav', '.aiff', '.mp3']).
                                    If not provided, it will return all files.

Returns:
- df (pd.DataFrame): A DataFrame containing the Path, Name, file_name, and file size columns.
- fre_tab (pd.DataFrame): A frequency table with the count and size of each file extension."""

def _filefinder_by_EXT_GET_df(my_folder_path, file_extensions):
    """
    This function searches the provided folder path for all specified music file extensions (case insensitive),
    or, if no file extensions are provided, it will return all files regardless of extension.
    
    Filters out unwanted files (starting with '._' and '.DS'), and returns a DataFrame containing the file path,
    the base name without extension ('Name'), the full file name ('file_name'), and the size in MB.
    
    It also includes a progress tracker (TQM) for better feedback and handles mixed case extensions.
    
    Parameters:
    - my_folder_path (str): The folder path where the search should be performed.
    - file_extensions (list, optional): A list of file extensions to search for (e.g., ['.wav', '.aiff', '.mp3']).
                                        If not provided, it will return all files.
    
    Returns:
    - df (pd.DataFrame): A DataFrame containing the Path, Name, file_name, and file size columns.
    - fre_tab (pd.DataFrame): A frequency table with the count and size of each file extension.
    """
    
    # Initialize empty DataFrame
    df = pd.DataFrame(columns=['Path', 'Name', 'file_name', 'Size (MB)', 'Extension'])
    
    # Check if the folder exists and is a directory
    if not os.path.exists(my_folder_path):
        print(f"Error: The folder path '{my_folder_path}' does not exist.")
        return df, pd.DataFrame()  # Return empty DataFrame and frequency table
    
    if not os.path.isdir(my_folder_path):
        print(f"Error: The provided path '{my_folder_path}' is not a directory.")
        return df, pd.DataFrame()  # Return empty DataFrame and frequency table

    # Normalize extensions to lowercase if provided, otherwise set to None to include all files
    if file_extensions:
        file_extensions = [ext.lower() for ext in file_extensions]

    # List to store file details
    file_list = []

    # Total number of files to process for TQM bar
    total_files = sum([len(files) for r, d, files in os.walk(my_folder_path)])

    try:
        # Walk through the directory with TQM progress bar
        with tqdm(total=total_files, desc="Searching for Files", unit="files") as pbar:
            for root, dirs, files in os.walk(my_folder_path):
                for file in files:
                    # Get file extension and ensure mixed-case matching
                    ext = os.path.splitext(file)[1].lower()
                    
                    # Check if the extension matches the specified ones, or if no extensions are provided, include all
                    if not file_extensions or ext in file_extensions:
                        try:
                            file_path = os.path.join(root, file)
                            file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert to MB
                            file_name_without_ext = os.path.splitext(file)[0]  # Get basename without extension
                            file_list.append({
                                'Path': file_path, 
                                'Name': file_name_without_ext, 
                                'file_name': file, 
                                'Size (MB)': file_size,
                                'Extension': ext
                            })
                        except FileNotFoundError as e:
                            # Gracefully handle the missing file scenario and log the error
                            print(f"Skipping file: {file_path}, reason: {e}")
                    pbar.update(1)
        
        # Create a DataFrame from the file list
        if file_list:
            df = pd.DataFrame(file_list)
    
    except PermissionError:
        print(f"Error: Permission denied while accessing '{my_folder_path}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    # Omit unwanted files that start with '._' or '.DS'
    df = df[~df['file_name'].str.startswith('._')].copy()
    df = df[~df['file_name'].str.startswith('.DS')].copy()

    # Check if the DataFrame is not empty before proceeding with the frequency table
    if not df.empty:
        # Create frequency table with the total size per extension
        fre_tab = df.groupby('Extension').agg(frequency=('Extension', 'size'),
                                              total_size_in_mb=('Size (MB)', 'sum')).reset_index()

        # Calculate grand total sizes
        grand_total_size_mb = df['Size (MB)'].sum()
        grand_total_size_bytes = grand_total_size_mb * (1024 * 1024)
        grand_total_size_gb = grand_total_size_mb / 1024
    else:
        fre_tab = pd.DataFrame()
        grand_total_size_mb = 0
        grand_total_size_bytes = 0
        grand_total_size_gb = 0

    # Display output format as requested
    print(f"ATTN ::: <E>  AFTER making sure that you have assigned the DIRECTORY PATH to ::: var ::: {my_folder_path}")
    print(f"***df*** will be returned having ::: {len(df)}  rows, write df in next cell to see your DATA FRAME\n")
    print(f"second part FREQUENCIES OF df :::\n")
    print(f"Grand Total Size in MB: {grand_total_size_mb:.3f}")
    print(f"Grand Total Size in Bytes: {grand_total_size_bytes:.3f}")
    print(f"Grand Total Size in GB: {grand_total_size_gb:.3f}\n")
    print(f" FREQUENCY TABLE::: \n")
    print(fre_tab)

    return df, fre_tab
# -----######-----######-----######-----######-----######-----######-----
# CHECK THAT AIFF FILES ARE IN CORRECT FORMAT OR REEFORMAT 
# -----######-----######-----######-----######-----######-----######-----



import os
from pydub import AudioSegment
from pydub.utils import mediainfo
import pandas as pd
import mutagen
from mutagen.aiff import AIFF

def analyze_and_downsize_aiff(folder_path, target_sample_rate=44100, target_bit_depth=16):
    # Dictionary to store combination frequencies
    combination_frequency = {}

    # Walk through all subfolders
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".aiff"):
                file_path = os.path.join(root, file)
                try:
                    info = mediainfo(file_path)
                    sample_rate = int(info.get('sample_rate', 0))
                    bit_depth = int(info.get('bits_per_sample', 0))

                    # Record the current combination
                    combination = (sample_rate, bit_depth)
                    combination_frequency[combination] = combination_frequency.get(combination, 0) + 1

                    # Check if downsizing is needed
                    if sample_rate != target_sample_rate or bit_depth != target_bit_depth:
                        print(f"{file} requires downsizing: Sample Rate={sample_rate}, Bit Depth={bit_depth}")
                        proceed = input("Enter 'y' to proceed with downsizing: ").strip().lower()
                        if proceed == 'y':
                            downsize_aiff(file_path, target_sample_rate, target_bit_depth)

                except Exception as e:
                    print(f"Error processing file {file}: {e}")

    # Convert results to DataFrame for readability
    df = pd.DataFrame(
        [(sr, bd, count) for (sr, bd), count in combination_frequency.items()],
        columns=['Sample Rate (Hz)', 'Bit Depth', 'Count']
    )
    df.sort_values(by='Count', ascending=False, inplace=True)
    return df

def downsize_aiff(file_path, target_sample_rate, target_bit_depth):
    try:
        audio = AudioSegment.from_file(file_path, format="aiff")
        downsized_audio = audio.set_frame_rate(target_sample_rate).set_sample_width(target_bit_depth // 8)
        
        # Preserve metadata
        original_metadata = mutagen.File(file_path)
        output_file_path = file_path.replace(".aiff", "_downsized.aiff")
        downsized_audio.export(output_file_path, format="aiff")

        # Restore metadata
        downsized_file = AIFF(output_file_path)
        for key, value in original_metadata.items():
            downsized_file[key] = value
        downsized_file.save()
        print(f"Successfully downsized {file_path} to {output_file_path} with metadata preserved")
    except Exception as e:
        print(f"Error downsizing file {file_path}: {e}")



##### COMM ::: _1_ MSG_AUDIO general ATTRIBUTES
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----

import os
import wave
import aifc
import pandas as pd
from tqdm import tqdm

def _convert_size(size_bytes):
    """Convert file size to a human-readable format."""
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int((size_bytes).bit_length() - 1) // 10
    p = 1024 ** i
    return f"{size_bytes / p:.2f} {size_name[i]}"

def _audio_attr_extract_11_INFO_AIFF(df, audio_extensions):
    """
    Extract key attributes from audio files (WAV and AIFF), including duration, sample rate, 
    number of channels, file size, and number of frames. Append this information to the 
    corresponding rows of the DataFrame, with TQM progress bar and size calculation.

    Parameters:
        df (pd.DataFrame): The DataFrame containing a 'Path' column with the audio file paths.
        audio_extensions (list): List of supported audio file extensions.

    Returns:
        pd.DataFrame: The DataFrame with appended audio attribute columns.
    """
    # Initialize columns for the audio attributes
    df['dur_seconds'] = None
    df['dur_min'] = None
    df['sr'] = None
    df['bit_depth'] = None
    df['bit_rate'] = None
    df['channels'] = None
    df['file_size'] = None
    df['file_size_human'] = None
    df['num_frames'] = None
    df['error'] = None
    
    # Iterate over the DataFrame rows with TQM progress bar
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Audio file Attributes"):
        file_path = row['Path']
        audio_attributes = {
            'dur_seconds': None,
            'dur_min': None,
            'sr': None,
            'bit_depth': None,
            'channels': None,
            'file_size': None,
            'file_size_human': None,
            'num_frames': None,
            'error': None
        }

        # Ensure the file exists
        if not os.path.isfile(file_path):
            df.at[index, 'error'] = "File does not exist"
            continue
        
        # Check file extension
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension not in [ext.lower() for ext in audio_extensions]:
            df.at[index, 'error'] = "Unsupported audio file extension"
            continue
        
        try:
            # Get file size in bytes
            file_size_bytes = os.path.getsize(file_path)
            audio_attributes['file_size'] = file_size_bytes
            audio_attributes['file_size_human'] = _convert_size(file_size_bytes)
            
            # Handle WAV files
            if file_extension in ['.wav', '.WAV']:
                with wave.open(file_path, 'rb') as audio_file:
                    audio_attributes['sr'] = audio_file.getframerate()
                    audio_attributes['channels'] = audio_file.getnchannels()
                    audio_attributes['num_frames'] = audio_file.getnframes()
                    duration_seconds = audio_attributes['num_frames'] / float(audio_attributes['sr'])
                    audio_attributes['dur_seconds'] = duration_seconds
                    audio_attributes['dur_min'] = duration_seconds / 60
                    audio_attributes['bit_depth'] = audio_file.getsampwidth() * 8  # Sample width (bytes) to bits
            
            # Handle AIFF files
            elif file_extension in ['.aif', '.aiff']:
                with aifc.open(file_path, 'rb') as audio_file:
                    audio_attributes['sr'] = audio_file.getframerate()
                    audio_attributes['channels'] = audio_file.getnchannels()
                    audio_attributes['num_frames'] = audio_file.getnframes()
                    duration_seconds = audio_attributes['num_frames'] / float(audio_attributes['sr'])
                    audio_attributes['dur_seconds'] = duration_seconds
                    audio_attributes['dur_min'] = duration_seconds / 60
                    audio_attributes['bit_depth'] = audio_file.getsampwidth() * 8  # Sample width (bytes) to bits
            
            # Populate the DataFrame
            for attr, value in audio_attributes.items():
                df.at[index, attr] = value

        except Exception as e:
            df.at[index, 'error'] = f"Unexpected error: {str(e)}"
    
    return df

# -----######-----######-----######-----######-----######-----######-----
# LUFS
# -----######-----######-----######-----######-----######-----######-----
import numpy as np
import pandas as pd
from pydub import AudioSegment
from pyloudnorm import Meter
from tqdm import tqdm

def compute_lufs_for_paths_AIFF(paths):
    # Create a loudness meter (rate will be updated for each file)
    meter = Meter(rate=44100)  # default rate, will be changed for each file

    lufs_results = []

    # Wrap your loop with tqdm for a progress bar
    for file_path in tqdm(paths, desc="Computing LUFS", unit="file"):

        try:
            # Load the audio file using pydub
            audio = AudioSegment.from_file(file_path)

            # Convert audio to WAV format and get channels data
            samples = np.array(audio.get_array_of_samples())

            # Convert integer samples to floating point and normalize
            samples = samples / (2**15)

            # Check if stereo or mono
            if audio.channels == 2:
                samples = samples.reshape((-1, 2))
            else:
                samples = samples.reshape((-1, 1))

            # Update the sample rate of the meter
            meter.rate = audio.frame_rate

            # Compute LUFS
            loudness = meter.integrated_loudness(samples)

            lufs_results.append(round(loudness, 3))

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            lufs_results.append(None)  # Append None for the failed computation, keeping the list lengths in sync

    return lufs_results

# -----######-----###### LUFS Mapping Function -----######-----######
def _all_values_CREATE_12_LUFS_categories(lufs_value):
    """
    Maps LUFS values to energy levels.

    Parameters:
    lufs_value (float): The LUFS value.

    Returns:
    str: Energy level code corresponding to LUFS value.
    """
    if lufs_value is None:
        return None
    elif lufs_value <= -18:
        return 'LuA'
    elif -18 < lufs_value <= -16:
        return 'LuB'
    elif -16 < lufs_value <= -14:
        return 'LuC'
    elif -14 < lufs_value <= -12:
        return 'LuD'
    elif -12 < lufs_value <= -10:
        return 'Lue'
    else:
        return 'LuF'

####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----
# BPM dynamic vs normal 
# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----
# 0_FNS: Core functions for BPM variation detection in AIFF files using DF attributes, TQDM, 
# BPM Consistency Index, and configurable exclusion of track intros/outros

import numpy as np
import pandas as pd
import librosa
from tqdm import tqdm  # For progress bar
from collections import Counter

def _bpm_2409_i1_GET_bpm_variation(
    filepath: str,
    target_sr: int = None,
    window_sec: float = 10.0,
    hop_sec: float = 5.0,
    exclude_start_pct: float = 0.1,
    exclude_end_pct: float = 0.1
):
    """
    Analyze an AIFF audio file to compute BPM variation metrics and a single BPM Consistency Index,
    excluding a configurable percentage of the track from both the start and end (to avoid intros/outros).
    
    The function loads the file using the provided sample rate (if any), normalizes the audio,
    excludes the specified portions, splits the remaining audio into overlapping windows, and computes
    the BPM for each segment. BPM values are rounded and aggregated to calculate the BPM Consistency Index
    (percentage of windows with the dominant BPM).
    
    Parameters:
        filepath (str): Path to the AIFF file.
        target_sr (int): Sample rate from your DataFrame. If None, the file's native rate is used.
        window_sec (float): Duration in seconds for each analysis window (default: 10 sec).
        hop_sec (float): Hop duration in seconds between windows (default: 5 sec).
        exclude_start_pct (float): Percentage of the track to exclude from the start (default: 0.1 or 10%).
        exclude_end_pct (float): Percentage of the track to exclude from the end (default: 0.1 or 10%).
    
    Returns:
        dict: BPM variation metrics including:
            - 'mean_bpm': Mean BPM across windows.
            - 'std_bpm': Standard deviation of BPM.
            - 'min_bpm': Minimum BPM.
            - 'max_bpm': Maximum BPM.
            - 'variation_percentage': (std_bpm / mean_bpm * 100).
            - 'dominant_bpm': The most frequent rounded BPM value.
            - 'bpm_consistency': Percentage of windows with the dominant BPM (the single pointer).
    """
    try:
        y, sr = librosa.load(filepath, sr=target_sr)
    except Exception as e:
        # Return NaN metrics if file loading fails
        return {
            'mean_bpm': np.nan,
            'std_bpm': np.nan,
            'min_bpm': np.nan,
            'max_bpm': np.nan,
            'variation_percentage': np.nan,
            'dominant_bpm': np.nan,
            'bpm_consistency': np.nan
        }
    
    # Normalize the audio in memory
    if np.max(np.abs(y)) > 0:
        y = y / np.max(np.abs(y))
    
    # Exclude intro and outro portions based on specified percentages
    total_samples = len(y)
    start_idx = int(total_samples * exclude_start_pct)
    end_idx = int(total_samples * (1 - exclude_end_pct))
    y = y[start_idx:end_idx]
    
    window_length = int(window_sec * sr)
    hop_length = int(hop_sec * sr)
    bpm_values = []
    
    # Process the audio in overlapping windows
    for start in range(0, len(y) - window_length + 1, hop_length):
        segment = y[start:start + window_length]
        # Attempt using the updated API; fall back if not available.
        try:
            tempo = librosa.feature.rhythm.tempo(y=segment, sr=sr, aggregate=np.median)
        except AttributeError:
            tempo = librosa.beat.tempo(y=segment, sr=sr, aggregate=np.median)
        bpm_values.append(tempo[0])
    
    bpm_array = np.array(bpm_values)
    mean_bpm = np.mean(bpm_array)
    std_bpm = np.std(bpm_array)
    min_bpm = np.min(bpm_array)
    max_bpm = np.max(bpm_array)
    variation_percentage = (std_bpm / mean_bpm * 100) if mean_bpm != 0 else 0
    
    # Aggregate the BPM values by rounding to the nearest integer and compute frequency distribution
    rounded_bpms = [round(b) for b in bpm_values] if bpm_values else []
    counter = Counter(rounded_bpms)
    if counter:
        dominant_bpm, dominant_count = counter.most_common(1)[0]
        total_count = sum(counter.values())
        bpm_consistency = dominant_count / total_count * 100
    else:
        dominant_bpm = np.nan
        bpm_consistency = np.nan
    
    return {
        'mean_bpm': mean_bpm,
        'std_bpm': std_bpm,
        'min_bpm': min_bpm,
        'max_bpm': max_bpm,
        'variation_percentage': variation_percentage,
        'dominant_bpm': dominant_bpm,
        'bpm_consistency': bpm_consistency
    }

def _df_bpm_2409_i1_GET_df_bpm_variation(
    input_df: pd.DataFrame,
    path_column: str = 'Path',
    sr_column: str = 'sr',
    window_sec: float = 10.0,
    hop_sec: float = 5.0,
    exclude_start_pct: float = 0.1,
    exclude_end_pct: float = 0.1
) -> pd.DataFrame:
    """
    Process a DataFrame of AIFF file paths and append BPM variation metrics including the BPM Consistency Index.
    Allows exclusion of a configurable percentage of the track's start and end to avoid distorting intros/outros.
    
    For each file in the specified column, the function uses the sample rate provided in the DataFrame
    to compute BPM metrics and appends the following new columns:
        - 'mean_bpm'
        - 'std_bpm'
        - 'min_bpm'
        - 'max_bpm'
        - 'variation_percentage'
        - 'dominant_bpm'
        - 'bpm_consistency'
    
    Parameters:
        input_df (pd.DataFrame): DataFrame containing file attribute columns.
        path_column (str): Column name with file paths (default: 'Path').
        sr_column (str): Column name with sample rate (default: 'sr').
        window_sec (float): Analysis window duration in seconds.
        hop_sec (float): Hop duration in seconds between windows.
        exclude_start_pct (float): Percentage of the track to exclude from the start (default: 0.1).
        exclude_end_pct (float): Percentage of the track to exclude from the end (default: 0.1).
    
    Returns:
        pd.DataFrame: The original DataFrame with BPM variation metrics appended.
    """
    results = {
        'mean_bpm': [],
        'std_bpm': [],
        'min_bpm': [],
        'max_bpm': [],
        'variation_percentage': [],
        'dominant_bpm': [],
        'bpm_consistency': []
    }
    
    # Iterate over each file path with a TQDM progress bar
    for idx, row in tqdm(input_df.iterrows(), total=input_df.shape[0], desc="Processing BPM Dynamic"):
        file_path = row[path_column]
        target_sr = int(row[sr_column]) if pd.notna(row[sr_column]) else None
        bpm_result = _bpm_2409_i1_GET_bpm_variation(
            file_path,
            target_sr=target_sr,
            window_sec=window_sec,
            hop_sec=hop_sec,
            exclude_start_pct=exclude_start_pct,
            exclude_end_pct=exclude_end_pct
        )
        results['mean_bpm'].append(bpm_result['mean_bpm'])
        results['std_bpm'].append(bpm_result['std_bpm'])
        results['min_bpm'].append(bpm_result['min_bpm'])
        results['max_bpm'].append(bpm_result['max_bpm'])
        results['variation_percentage'].append(bpm_result['variation_percentage'])
        results['dominant_bpm'].append(bpm_result['dominant_bpm'])
        results['bpm_consistency'].append(bpm_result['bpm_consistency'])
    
    # Append new columns to a copy of the original DataFrame
    input_df = input_df.copy()
    input_df['mean_bpm'] = results['mean_bpm']
    input_df['std_bpm'] = results['std_bpm']
    input_df['min_bpm'] = results['min_bpm']
    input_df['max_bpm'] = results['max_bpm']
    input_df['variation_percentage'] = results['variation_percentage']
    input_df['dominant_bpm'] = results['dominant_bpm']
    input_df['bpm_consistency'] = results['bpm_consistency']
    
    return input_df

# 0_FNS: Core Function to Categorize bpm_consistency
# ----------------------------------------------------
import numpy as np
import pandas as pd

def _cat_0204_bpm_consistency_GET_cat(df: pd.DataFrame) -> pd.DataFrame:
    """
    Categorizes the 'bpm_consistency' column in the provided DataFrame.
    
    The categorization is as follows:
      - 0 <= bpm_consistency < 50   : 'D_9'
      - 50 <= bpm_consistency < 85  : 'D_6'
      - 85 <= bpm_consistency < 95  : 'D_3'
      - 95 <= bpm_consistency < 98  : 'D_1'
      - 98 <= bpm_consistency <= 100: 'D_0'
    
    Parameters:
      df (pd.DataFrame): DataFrame with a 'bpm_consistency' column.
    
    Returns:
      pd.DataFrame: The DataFrame with an additional column 'bpm_consistency_cat'.
    """
    # #### TQM BAR: [==============================] Ensuring Quality Metrics
    
    conditions = [
        (df['bpm_consistency'] < 50),
        (df['bpm_consistency'] >= 50) & (df['bpm_consistency'] < 85),
        (df['bpm_consistency'] >= 85) & (df['bpm_consistency'] < 95),
        (df['bpm_consistency'] >= 95) & (df['bpm_consistency'] < 98),
        (df['bpm_consistency'] >= 98) & (df['bpm_consistency'] <= 100)
    ]
    choices = ['D_9', 'D_6', 'D_3', 'D_1', 'D_0']
    
    # Apply categorization using numpy.select
    df['bpm_consistency_cat'] = np.select(conditions, choices, default='Unknown')
    return df



####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----
# METADATA ::: 1 = title
# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----


######## 
from mutagen import File
from tqdm import tqdm

def _titile_0204_id3_filefallback_GET_df_with_titile(df, var, btw_front, btw_back):
    import os

    # Storage
    titiles = []
    title_files = []

    for path in tqdm(df['Path'], desc="Extracting ID3 Titles"):
        title_from_tag = None
        try:
            audio = File(path)
            if audio and hasattr(audio, "tags") and audio.tags:
                tag = audio.tags.get("TIT2")
                if tag:
                    title_from_tag = str(tag).strip()
        except Exception:
            title_from_tag = None

        if title_from_tag:
            titiles.append(title_from_tag)
            title_files.append("ID3TAGS")
        else:
            titiles.append(None)
            title_files.append("FILE_NAME")

    # Append interim results
    df['titile'] = titiles
    df['title_file'] = title_files

    # Define fallback function (embedded for independence)
    def _file_extract_from_file_name_(df, var, btw_front, btw_back):
        empty_values = [None, "", "None", "NAN", "NaN", "nan","Error: argument of type 'NoneType' is not iterable"]
        missing_title_idx = df[f'{var}'].isin(empty_values) | df[f'{var}'].isnull()

        def extract_title_from_temp_id(temp_id):
            if isinstance(temp_id, str) and f"{btw_front}" in temp_id and f"{btw_back}" in temp_id:
                start = temp_id.find(f"{btw_front}") + len(btw_front)
                end = temp_id.find(f"{btw_back}", start)
                return temp_id[start:end].strip()
            return None

        df.loc[missing_title_idx, f'{var}'] = df.loc[missing_title_idx, 'temp_id'].apply(extract_title_from_temp_id)
        return df

    # Apply fallback where titile is still missing
    df_missing = df[df['titile'].isnull()].copy()
    if not df_missing.empty:
        df_missing['title'] = df_missing.get('title', None)  # fallback expects 'title' column
        df_fallback = _file_extract_from_file_name_(df_missing, var, btw_front, btw_back)
        df.loc[df_fallback.index, 'titile'] = df_fallback[var]

    return df

####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----
# # METADATA ::: 2 = artist
# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----
# GET ARTIST FROM ID3 OR FILENAME (W/ FALLBACK & SOURCE FLAG)
# -----######-----######-----######-----######-----######-----

from mutagen import File
from tqdm import tqdm

def _artist_0204_id3_filefallback_GET_df_with_artist(df, var, btw_front, btw_back):
    import os

    # Storage
    artists = []
    artist_sources = []

    for path in tqdm(df['Path'], desc="Extracting ID3 Artists"):
        artist_from_tag = None
        try:
            audio = File(path)
            if audio and hasattr(audio, "tags") and audio.tags:
                tag = audio.tags.get("TPE1")  # Artist tag
                if tag:
                    artist_from_tag = str(tag).strip()
        except Exception:
            artist_from_tag = None

        if artist_from_tag:
            artists.append(artist_from_tag)
            artist_sources.append("ID3TAGS")
        else:
            artists.append(None)
            artist_sources.append("FILE_NAME")

    # Append interim results
    df['artist'] = artists
    df['artist_file'] = artist_sources

    # Define fallback function (embedded for independence)
    def _file_extract_from_file_name_(df, var, btw_front, btw_back):
        empty_values = [None, "", "None", "NAN", "NaN", "nan","Error: argument of type 'NoneType' is not iterable"]
        missing_artist_idx = df[f'{var}'].isin(empty_values) | df[f'{var}'].isnull()

        def extract_artist_from_temp_id(temp_id):
            if isinstance(temp_id, str) and f"{btw_front}" in temp_id and f"{btw_back}" in temp_id:
                start = temp_id.find(f"{btw_front}") + len(btw_front)
                end = temp_id.find(f"{btw_back}", start)
                return temp_id[start:end].strip()
            return None

        df.loc[missing_artist_idx, f'{var}'] = df.loc[missing_artist_idx, 'temp_id'].apply(extract_artist_from_temp_id)
        return df

    # Apply fallback where artist is still missing
    df_missing = df[df['artist'].isnull()].copy()
    if not df_missing.empty:
        df_missing[var] = df_missing.get(var, None)  # fallback expects the target var
        df_fallback = _file_extract_from_file_name_(df_missing, var, btw_front, btw_back)
        df.loc[df_fallback.index, 'artist'] = df_fallback[var]

    return df

####
##
#


# # METADATA ::: 3 = LABEL
# -----######-----######-----######-----######-----######-----
# GET LABEL FROM ID3 OR FILENAME (W/ FALLBACK & SOURCE FLAG)
# -----######-----######-----######-----######-----######-----

from mutagen import File
from tqdm import tqdm

def _label_0204_id3_filefallback_GET_df_with_LABEL(df, var, btw_front, btw_back):
    import os

    # Storage
    labels = []
    label_sources = []

    for path in tqdm(df['Path'], desc="Extracting ID3 Labels"):
        label_from_tag = None
        try:
            audio = File(path)
            if audio and hasattr(audio, "tags") and audio.tags:
                tag = audio.tags.get("TPUB")  # Publisher tag (used for LABEL)
                if tag:
                    label_from_tag = str(tag).strip()
        except Exception:
            label_from_tag = None

        if label_from_tag:
            labels.append(label_from_tag)
            label_sources.append("ID3TAGS")
        else:
            labels.append(None)
            label_sources.append("FILE_NAME")

    # Append interim results
    df['LABEL'] = labels
    df['label_file'] = label_sources

    # Define fallback function (embedded for independence)
    def _file_extract_from_file_name_(df, var, btw_front, btw_back):
        empty_values = [None, "", "None", "NAN", "NaN", "nan","Error: argument of type 'NoneType' is not iterable"]
        missing_label_idx = df[f'{var}'].isin(empty_values) | df[f'{var}'].isnull()

        def extract_label_from_temp_id(temp_id):
            if isinstance(temp_id, str) and f"{btw_front}" in temp_id and f"{btw_back}" in temp_id:
                start = temp_id.find(f"{btw_front}") + len(btw_front)
                end = temp_id.find(f"{btw_back}", start)
                return temp_id[start:end].strip()
            return None

        df.loc[missing_label_idx, f'{var}'] = df.loc[missing_label_idx, 'temp_id'].apply(extract_label_from_temp_id)
        return df

    # Apply fallback where LABEL is still missing
    df_missing = df[df['LABEL'].isnull()].copy()
    if not df_missing.empty:
        df_missing[var] = df_missing.get(var, None)  # fallback expects the target var
        df_fallback = _file_extract_from_file_name_(df_missing, var, btw_front, btw_back)
        df.loc[df_fallback.index, 'LABEL'] = df_fallback[var]

    return df


####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----
# -----######-----######-----######-----######-----######-----
# GET GENRE FROM ID3 OR FILENAME (W/ FALLBACK & SOURCE FLAG)
# -----######-----######-----######-----######-----######-----

from mutagen import File
from tqdm import tqdm

def _genre_0204_id3_filefallback_GET_df_with_genre(df, var, btw_front, btw_back):
    import os

    genres = []
    genre_sources = []

    for path in tqdm(df['Path'], desc="Extracting ID3 Genres"):
        genre_from_tag = None
        try:
            audio = File(path)
            if audio and hasattr(audio, "tags") and audio.tags:
                tag = audio.tags.get("TCON")  # Genre tag
                if tag:
                    genre_from_tag = str(tag).strip()
        except Exception:
            genre_from_tag = None

        if genre_from_tag:
            genres.append(genre_from_tag)
            genre_sources.append("ID3TAGS")
        else:
            genres.append(None)
            genre_sources.append("FILE_NAME")

    df['genre'] = genres
    df['genre_file'] = genre_sources

    # Define fallback function (embedded)
    def _file_extract_from_file_name_(df, var, btw_front, btw_back):
        empty_values = [None, "", "None", "NAN", "NaN", "nan", "Error: argument of type 'NoneType' is not iterable"]
        missing_genre_idx = df[f'{var}'].isin(empty_values) | df[f'{var}'].isnull()

        def extract_genre_from_temp_id(temp_id):
            if isinstance(temp_id, str) and btw_front in temp_id and btw_back in temp_id:
                start = temp_id.find(btw_front) + len(btw_front)
                end = temp_id.find(btw_back, start)
                return temp_id[start:end].strip()
            return None

        df.loc[missing_genre_idx, f'{var}'] = df.loc[missing_genre_idx, 'temp_id'].apply(extract_genre_from_temp_id)
        return df

    # Apply fallback where genre is missing
    df_missing = df[df['genre'].isnull()].copy()
    if not df_missing.empty:
        df_missing[var] = df_missing.get(var, None)
        df_fallback = _file_extract_from_file_name_(df_missing, var, btw_front, btw_back)
        df.loc[df_fallback.index, 'genre'] = df_fallback[var]

    return df


####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----
# GET RELEASE YEAR FROM ID3 OR FILENAME (W/ FALLBACK & SOURCE FLAG)
# -----######-----######-----######-----######-----######-----

from mutagen import File
from tqdm import tqdm

def _relyear_0204_id3_filefallback_GET_df_with_rel_year(df, var, btw_front, btw_back):
    import os

    rel_years = []
    rel_year_sources = []

    for path in tqdm(df['Path'], desc="Extracting ID3 Release Year"):
        year_from_tag = None
        try:
            audio = File(path)
            if audio and hasattr(audio, "tags") and audio.tags:
                tag = audio.tags.get("TDRC")  # Recording time tag (usually YYYY)
                if tag:
                    year_from_tag = str(tag).strip()
                    if len(year_from_tag) >= 4:
                        year_from_tag = year_from_tag[:4]  # Extract only YYYY
        except Exception:
            year_from_tag = None

        if year_from_tag:
            rel_years.append(year_from_tag)
            rel_year_sources.append("ID3TAGS")
        else:
            rel_years.append(None)
            rel_year_sources.append("FILE_NAME")

    df['rel_year'] = rel_years
    df['rel_year_file'] = rel_year_sources

    # Define fallback function (embedded)
    def _file_extract_from_file_name_(df, var, btw_front, btw_back):
        empty_values = [None, "", "None", "NAN", "NaN", "nan", "Error: argument of type 'NoneType' is not iterable"]
        missing_year_idx = df[f'{var}'].isin(empty_values) | df[f'{var}'].isnull()

        def extract_year_from_temp_id(temp_id):
            if isinstance(temp_id, str) and btw_front in temp_id and btw_back in temp_id:
                start = temp_id.find(btw_front) + len(btw_front)
                end = temp_id.find(btw_back, start)
                return temp_id[start:end].strip()
            return None

        df.loc[missing_year_idx, f'{var}'] = df.loc[missing_year_idx, 'temp_id'].apply(extract_year_from_temp_id)
        return df

    # Apply fallback
    df_missing = df[df['rel_year'].isnull()].copy()
    if not df_missing.empty:
        df_missing[var] = df_missing.get(var, None)
        df_fallback = _file_extract_from_file_name_(df_missing, var, btw_front, btw_back)
        df.loc[df_fallback.index, 'rel_year'] = df_fallback[var]

    return df


####
##
#


# -----######-----######-----######-----######-----######-----
# GET MUSICAL KEY FROM ID3 OR FILENAME (W/ FALLBACK & SOURCE FLAG)
# -----######-----######-----######-----######-----######-----

from mutagen import File
from tqdm import tqdm

def _key_0204_id3_filefallback_GET_df_with_key(df, var, btw_front, btw_back):
    import os

    keys = []
    key_sources = []

    for path in tqdm(df['Path'], desc="Extracting ID3 Key"):
        key_from_tag = None
        try:
            audio = File(path)
            if audio and hasattr(audio, "tags") and audio.tags:
                tag = audio.tags.get("TKEY")  # Musical key tag
                if tag:
                    key_from_tag = str(tag).strip()
        except Exception:
            key_from_tag = None

        if key_from_tag:
            keys.append(key_from_tag)
            key_sources.append("ID3TAGS")
        else:
            keys.append(None)
            key_sources.append("FILE_NAME")

    df['KEY'] = keys
    df['key_file'] = key_sources

    # Define fallback function (embedded)
    def _file_extract_from_file_name_(df, var, btw_front, btw_back):
        empty_values = [None, "", "None", "NAN", "NaN", "nan", "Error: argument of type 'NoneType' is not iterable"]
        missing_key_idx = df[f'{var}'].isin(empty_values) | df[f'{var}'].isnull()

        def extract_key_from_temp_id(temp_id):
            if isinstance(temp_id, str) and btw_front in temp_id and btw_back in temp_id:
                start = temp_id.find(btw_front) + len(btw_front)
                end = temp_id.find(btw_back, start)
                return temp_id[start:end].strip()
            return None

        df.loc[missing_key_idx, f'{var}'] = df.loc[missing_key_idx, 'temp_id'].apply(extract_key_from_temp_id)
        return df

    # Apply fallback
    df_missing = df[df['KEY'].isnull()].copy()
    if not df_missing.empty:
        df_missing[var] = df_missing.get(var, None)
        df_fallback = _file_extract_from_file_name_(df_missing, var, btw_front, btw_back)
        df.loc[df_fallback.index, 'KEY'] = df_fallback[var]

    return df



####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----
# EXTRACT MIX NAME & REMIXER FROM TEMP_ID (FILENAME PATTERN)
# -----######-----######-----######-----######-----######-----

def _mixremix_0204_filename_extract_GET_df_mix_and_remixer(df):
    def extract_between(temp_id, front, back):
        if isinstance(temp_id, str) and front in temp_id and back in temp_id:
            start = temp_id.find(front) + len(front)
            end = temp_id.find(back, start)
            content = temp_id[start:end].strip('_ ').strip()
            return content if content else None
        return None

    df['mix_name'] = df['temp_id'].apply(lambda x: extract_between(x, 'MXkw_', 'KYkw_'))
    df['remixer'] = df['temp_id'].apply(lambda x: extract_between(x, 'RMkw_', 'LBkw_'))
    df['remixer'] = df['remixer'] + ' '+ df['mix_name']
    return df


####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----
# EXTRACT PURCHASE DATE (AFTER PYkw_) FROM TEMP_ID STRING
# -----######-----######-----######-----######-----######-----

import re
import pandas as pd

def _datepurch_0204_filename_extract_GET_df_with_date_purchased(df):
    def extract_purchase_date(temp_id):
        if isinstance(temp_id, str):
            match = re.search(r'PYkw_(\d{4})_(\d{2})_(\d{2})', temp_id)
            if match:
                try:
                    return pd.to_datetime(f"{match.group(1)}-{match.group(2)}-{match.group(3)}")
                except Exception:
                    return None
        return None

    df['date_purchased'] = df['temp_id'].apply(extract_purchase_date)
    return df


####
##
# ################### write back to ID3 tags

# -----######----- FUNCTION: _aiff_0102_i1_GET_update_remixer_tpe4_tag -----######-----
# -----######----- FUNCTION: _aiff_0102_i1_GET_update_remixer_tpe4_tag -----######-----
import mutagen
from mutagen.aiff import AIFF
from mutagen.id3 import TPE4
from tqdm import tqdm

def _aiff_0102_i1_GET_update_remixer_tpe4_tag(df):
    """
    Updates the 'Remixer' tag in each AIFF file specified in the DataFrame by writing the value 
    from the 'remixer' column (with underscores replaced by spaces) into the TPE4 frame
    (which Rekordbox uses for remix information).

    If a file already contains a TPE4 tag (i.e. a remixer is already set), the file is skipped.

    Parameters:
        df (pandas.DataFrame): DataFrame with columns 'remixer' and 'Path'
    """
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Writing Remixer"):
        file_path = row['Path']
        # Replace underscores with spaces in the remixer value
        remixer_val = str(row['remixer']).replace("_", " ")
        
        try:
            # Load the AIFF file
            aiff_file = AIFF(file_path)
        except Exception as e:
            print(f"Error opening file {file_path}: {e}")
            continue
        
        # Add ID3 tags if they don't exist
        if aiff_file.tags is None:
            aiff_file.add_tags()
        
        # Check if TPE4 tag is already present and has text
        existing_tpe4 = aiff_file.tags.getall("TPE4")
        if existing_tpe4 and any(frame.text for frame in existing_tpe4):
            print(f"Skipping file ::: TPE4 tag already exists.")
            continue
        
        # Add new TPE4 frame with the cleaned remixer value
        aiff_file.tags.add(TPE4(encoding=3, text=[remixer_val]))
        
        try:
            aiff_file.save()
        except Exception as e:
            print(f"Error saving file {file_path}: {e}")



####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----
# -----######-----###### 0_FNS: Primary Function(s) -----######-----######
# -----######-----###### 0_FNS: Primary Function(s) -----######-----######
import os
from mutagen.aiff import AIFF
from mutagen.id3 import TCON
from tqdm import tqdm

def _write_genre_id3_bulk(df, path_col='Path', genre_col='genre'):
    """
    Updates the ID3 genre tag (TCON) for AIFF files specified in the DataFrame.
    Only processes rows where the 'genre_file' column equals "FILE_NAME".
    
    Parameters:
        df (pandas.DataFrame): DataFrame containing:
            - 'genre': The genre value to be written.
            - 'genre_file': Contains two labels; only rows with "FILE_NAME" are processed.
            - 'Path': The file path to the corresponding AIFF file.
        path_col (str): Column name for file paths (default 'Path').
        genre_col (str): Column name for genre values (default 'genre').
    
    Returns:
        int: The total number of files successfully processed.
    """
    # Filter the DataFrame to only process rows with genre_file equal to "FILE_NAME"
    df_filtered = df[df['genre_file'] == "FILE_NAME"].copy()
    success_count = 0

    # Iterate over the filtered DataFrame rows with a TQM progress bar
    for _, row in tqdm(df_filtered.iterrows(), total=len(df_filtered), desc="Processing AIFF files"):
        file_path = row[path_col]
        genre_value = row[genre_col]
        
        # Check if the file exists
        if not os.path.isfile(file_path):
            print(f"File not found: {file_path}")
            continue
        
        try:
            # Load the AIFF file
            audio = AIFF(file_path)
            
            # Add ID3 tags if they are missing
            if not hasattr(audio, "tags") or audio.tags is None:
                audio.add_tags()
            
            # Remove any existing genre tags (TCON frames)
            if "TCON" in audio.tags:
                del audio.tags["TCON"]
            
            # Add the new genre tag with UTF-8 encoding (encoding=3)
            audio.tags.add(TCON(encoding=3, text=[genre_value]))
            
            # Save the updated tags back to the file
            audio.save()
            success_count += 1
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
    
    print(f"Total files processed: {success_count}")
    return success_count



####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----
# -----######-----###### 0_FNS: Primary Function(s) -----######-----######
import os
from mutagen.aiff import AIFF
from mutagen.id3 import TPUB
from tqdm import tqdm

def _write_label_id3_bulk(df, path_col='Path', label_col='LABEL'):
    """
    Updates the ID3 label tag (TPUB) for AIFF files specified in the DataFrame.
    Only processes rows where the 'label_file' column equals "FILE_NAME".
    
    Parameters:
        df (pandas.DataFrame): DataFrame containing:
            - 'LABEL': The label value to be written.
            - 'label_file': Contains two labels; only rows with "FILE_NAME" are processed.
            - 'Path': The file path to the corresponding AIFF file.
        path_col (str): Column name for file paths (default 'Path').
        label_col (str): Column name for label values (default 'LABEL').
    
    Returns:
        int: The total number of files successfully processed.
    """
    # Filter the DataFrame to only process rows with label_file equal to "FILE_NAME"
    df_filtered = df[df['label_file'] == "FILE_NAME"].copy()
    success_count = 0

    # Iterate over the filtered DataFrame rows with a TQM progress bar
    for _, row in tqdm(df_filtered.iterrows(), total=len(df_filtered), desc="Processing AIFF files for label"):
        file_path = row[path_col]
        label_value = row[label_col]
        
        # Check if the file exists
        if not os.path.isfile(file_path):
            print(f"File not found: {file_path}")
            continue
        
        try:
            # Load the AIFF file
            audio = AIFF(file_path)
            
            # Add ID3 tags if they are missing
            if not hasattr(audio, "tags") or audio.tags is None:
                audio.add_tags()
            
            # Remove any existing label tags (TPUB frames)
            if "TPUB" in audio.tags:
                del audio.tags["TPUB"]
            
            # Add the new label tag with UTF-8 encoding (encoding=3)
            audio.tags.add(TPUB(encoding=3, text=[label_value]))
            
            # Save the updated tags back to the file
            audio.save()
            success_count += 1
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
    
    print(f"Total files processed for label: {success_count}")
    return success_count



####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----



####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----



####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----



####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----



####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----



####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 



# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----



####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----



####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----



####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----



####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----



####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----



####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----



####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----



####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----



####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# 
# -----######-----######-----######-----######-----######-----######-----



####
##
#

# -----######-----######-----######-----######-----######-----######-----
# 
