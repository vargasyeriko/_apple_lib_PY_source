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
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing Audio Files"):
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
