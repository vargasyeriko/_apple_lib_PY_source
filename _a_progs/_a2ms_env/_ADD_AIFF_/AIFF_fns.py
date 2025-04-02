# -----######-----######-----######-----######-----######-----######-----
# _pathfinder_0104_navigator_GET_final_path
# -----######-----######-----######-----######-----######-----######-----
# -----######-----######-----######-----######-----######-----######-----
# _pathfinder_0104_navigator_GET_final_path
# -----######-----######-----######-----######-----######-----######-----

import os

def _pathfinder_0104_navigator_GET_final_path():
    import os

    home = os.path.expanduser("~")

    # Step 1 - Choose path method
    print("\nWhere would you like to start?")
    print("1. Desktop")
    print("2. Downloads")
    print("3. Enter path manually")

    base_choice = input("Enter 1, 2 or 3: ").strip()

    if base_choice == "1":
        base_path = os.path.join(home, "Desktop")
    elif base_choice == "2":
        base_path = os.path.join(home, "Downloads")
    elif base_choice == "3":
        custom_path = input("\n🔠 Type or paste the full path: ").strip()
        if not os.path.exists(custom_path):
            print("❌ That path does not exist. Exiting.")
            return None
        base_path = custom_path
    else:
        print("❌ Invalid selection. Exiting.")
        return None

    print(f"\n🧭 Base path set to: {base_path}")

    # Step 2 - Ask for search keyword
    search_input = input("\n🔍 Enter keyword to look for in folders/files (leave blank to skip search): ").strip().lower()

    if search_input:
        possible_matches = []
        print("\n📂 Searching for matches...\n")

        for root, dirs, files in os.walk(base_path):
            for d in dirs:
                if search_input in d.lower():
                    possible_matches.append(os.path.join(root, d))
            for f in files:
                if search_input in f.lower():
                    possible_matches.append(os.path.join(root, f))

        if not possible_matches:
            print("❌ No matches found.")
            return None

        # Step 3 - Show matches and confirm
        for i, match in enumerate(possible_matches):
            print(f"{i+1}: {match}")
            confirm = input("Is this the one? (y/n): ").strip().lower()
            if confirm == 'y':
                print(f"\n✅ Path confirmed: {match}")
                return match

        print("\n❌ No path confirmed.")
        return None

    else:
        # No keyword provided, confirm base path directly
        confirm = input(f"\nDo you want to use this path? → {base_path} (y/n): ").strip().lower()
        if confirm == 'y':
            print(f"\n✅ Path confirmed: {base_path}")
            return base_path
        else:
            print("❌ Cancelled.")
            return None


#-----######-----######-----###### FUNCTION -----######-----######-----######
def _hash_0912_df_ITERATE_APPEND_hash(df):
    """
    Iterates through a DataFrame, hashes audio content from the 'Path' column,
    and appends the hashes as a new column 'Audio_Hash'.
    
    Parameters:
    - df: DataFrame with a 'Path' column containing file paths
    
    Modifies:
    - Appends 'Audio_Hash' column to the original DataFrame
    """
    hashes = []

    for idx, row in df.iterrows():
        file_path = row['Path']

        try:
            # Extract raw audio hash
            command = [
                "ffmpeg", "-i", file_path, 
                "-map", "0:a:0", "-f", "s16le", "-acodec", "pcm_s16le", "-vn", "pipe:1"
            ]
            process = subprocess.run(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
            )
            audio_hash = hashlib.sha256(process.stdout).hexdigest()
            hashes.append(audio_hash)
            print(f"[Success] Hashed: {file_path}")

        except subprocess.CalledProcessError as e:
            error_msg = f"FFmpeg failed: {e.stderr.decode('utf-8').strip()}"
            print(f"[Error] {error_msg}")
            hashes.append(error_msg)

        except Exception as e:
            error_msg = f"Processing failed: {e}"
            print(f"[Error] {error_msg}")
            hashes.append(error_msg)

    # Append new column to DataFrame
    df['Audio_Hash'] = hashes

#####################################
##################################### check AIFF formats to 44.1 16
#####################################

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





#####################################
#####################################
#####################################


# -----######-----######-----###### FUNCTION -----######-----######-----######
def _write_comment_2712_id3_SET_tag_bulk(df, path_col, comment_col):
    """
    Writes comments to the ID3 tags of AIFF files based on a DataFrame.
    
    Parameters:
    - df: DataFrame containing file paths and comments.
    - path_col: Column name in the DataFrame containing AIFF file paths.
    - comment_col: Column name in the DataFrame containing comments to write.

    Returns:
    - DataFrame: Updated with a 'status' column indicating success or error messages.
    """
    import mutagen
    from mutagen.aiff import AIFF
    from mutagen.id3 import ID3, COMM
    
    results = []
    
    for index, row in df.iterrows():
        aiff_path = row[path_col]
        comment_text = row[comment_col]
        
        try:
            # Load the AIFF file
            audio = AIFF(aiff_path)
            
            # Add ID3 tag if not already present
            if not hasattr(audio, "tags") or audio.tags is None:
                audio.add_tags()
            
            # Remove existing comments
            if "COMM" in audio.tags:
                del audio.tags["COMM"]
            
            # Add new comment
            audio.tags.add(COMM(encoding=3, lang='eng', desc='', text=comment_text))
            
            # Save changes
            audio.save()
            
            results.append("Success: Comment added")
        except Exception as e:
            results.append(f"Error: {e}")
    
    # Add results to DataFrame
    df["status"] = results
    return df



#####################################
#####################################
#####################################
def process_date_column(df):
    df['rel_date'] = 'None'
    # Ensure 'rel_date' is in datetime format (handle NaT gracefully)
    df['rel_date'] = pd.to_datetime(df['rel_date'], errors='coerce', format='%Y-%m-%d')

    # Create new columns with default values set to None
    df['rel_year'] = None
    df['rel_month'] = None
    df['rel_day'] = None
    df['rel_weekday'] = None

    # Extract year, month, day, and weekday where possible
    for index, row in df.iterrows():
        # If rel_date is not NaT (not empty or null)
        if pd.notnull(row['rel_date']):
            # Extract year
            df.at[index, 'rel_year'] = row['rel_date'].year

            # If we have a full date, extract the rest
            if row['rel_date'].month and row['rel_date'].day:
                df.at[index, 'rel_month'] = row['rel_date'].strftime('%b')  # Abbreviated month
                df.at[index, 'rel_day'] = row['rel_date'].day  # Day of the month
                df.at[index, 'rel_weekday'] = row['rel_date'].strftime('%a')  # Abbreviated weekday
        # If the date is NaT, the default 'None' values remain.

    return df





#####################################
############HASH#####################
#####################################

#-----######-----######-----###### IMPORT STATEMENTS -----######-----######-----######
import hashlib
import subprocess
import pandas as pd

#-----######-----######-----###### FUNCTION -----######-----######-----######
def _hash_bulk_2812_audio_GET_df_hashes(df):
    """
    Computes the hash of the actual audio content for each file in the DataFrame.
    Extracts raw PCM audio without headers or metadata.

    Parameters:
    - df: DataFrame with a 'Path' column containing file paths.

    Returns:
    - DataFrame: Original DataFrame with a new column 'audio_hash'.
    """
    # Ensure 'Path' column exists
    if 'Path' not in df.columns:
        raise ValueError("The DataFrame must contain a 'Path' column.")

    hashes = []

    for mp3_path in df['Path']:
        try:
            # Extract only raw audio with FFmpeg (16-bit PCM, stereo)
            command = [
                "ffmpeg", "-i", mp3_path, 
                "-map", "0:a:0",  # First audio stream only
                "-f", "s16le",  # Raw PCM format
                "-acodec", "pcm_s16le",  # 16-bit PCM
                "-vn",  # No video
                "pipe:1"
            ]

            # Run FFmpeg and capture audio output
            process = subprocess.run(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
            )

            # Compute the hash from the raw audio stream
            hash_audio_content = hashlib.sha256(process.stdout).hexdigest()

            hashes.append(hash_audio_content)
        except subprocess.CalledProcessError as e:
            # Capture FFmpeg error
            hashes.append(f"FFmpeg Error: {e.stderr.decode('utf-8').strip()}")
        except Exception as e:
            # Capture general error
            hashes.append(f"Error: {str(e)}")

    # Add the hashes to the DataFrame as a new column
    df['audio_hash'] = hashes
    return df

#-----######-----######-----###### RUNNING STATEMENTS -----######-----######-----######
# Example Usage:
# df = pd.DataFrame({"Path": ["file1.mp3", "file2.mp3", "file3.mp3"]})
# df = _hash_bulk_2812_audio_GET_df_hashes(df)
# print(df)






#####################################
##################################### PREPROCESS
#####################################

print("AIFF fns imported\n\n")