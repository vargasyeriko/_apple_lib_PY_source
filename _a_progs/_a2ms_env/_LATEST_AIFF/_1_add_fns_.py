# -----######----- FUNCTION: _write_2411_i1_SET_id3_tags_bulk -----######-----
import os
import pandas as pd
from mutagen.aiff import AIFF
from mutagen.id3 import COMM, TIT2, TPE1, TCON, TXXX
from tqdm import tqdm

def _write_2411_i1_SET_id3_tags_bulk(df, 
                                      path_col='Path', 
                                      comment_col='comment', 
                                      title_col='title', 
                                      artist_col='artist',
                                      genre_col='genre',
                                      label_col='label'):
    """
    Overwrites the comment, title, artist, genre, and label ID3 tags for AIFF files specified in the DataFrame.
    The function processes each file listed in the DataFrame and writes:
      - Comment from the comment column.
      - Title from the title column.
      - Artist from the artist column.
      - Genre from the genre column (using TCON).
      - Label from the label column (stored in a TXXX frame with description "LABEL").
      
    If any field is NaN, an empty string is used. The function ensures that ID3 tags are created if missing
    and removes any existing frames before adding new ones.
    
    Parameters:
        df (pandas.DataFrame): DataFrame containing:
            - 'comment': Comment text to be written.
            - 'title': Title text.
            - 'artist': Artist text.
            - 'genre': Genre text.
            - 'label': Label text.
            - 'Path': The file path to the corresponding AIFF file.
        path_col (str): Column name for file paths (default: 'Path').
        comment_col (str): Column name for comment texts (default: 'comment').
        title_col (str): Column name for title texts (default: 'title').
        artist_col (str): Column name for artist texts (default: 'artist').
        genre_col (str): Column name for genre texts (default: 'genre').
        label_col (str): Column name for label texts (default: 'label').
    
    Returns:
        int: The total number of files successfully processed.
    """
    success_count = 0

    # Iterate over DataFrame rows with a TQM progress bar
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Writing AIFF tags (comment/title/artist/genre/label)"):
        file_path = row[path_col]
        
        # Retrieve values from DataFrame; convert NaN to empty string if necessary
        comment_text = row[comment_col] if pd.notnull(row[comment_col]) else ""
        title_text   = row[title_col]   if pd.notnull(row[title_col])   else ""
        artist_text  = row[artist_col]  if pd.notnull(row[artist_col])  else ""
        genre_text   = row[genre_col]   if pd.notnull(row[genre_col])   else ""
        label_text   = row[label_col]   if pd.notnull(row[label_col])   else ""
        
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
            
            # Remove existing frames if present
            if "COMM" in audio.tags:
                del audio.tags["COMM"]
            if "TIT2" in audio.tags:
                del audio.tags["TIT2"]
            if "TPE1" in audio.tags:
                del audio.tags["TPE1"]
            if "TCON" in audio.tags:
                del audio.tags["TCON"]
            # Remove any existing TXXX frames that have the description "LABEL"
            for frame in audio.tags.getall("TXXX"):
                if frame.desc == "LABEL":
                    audio.tags.del(frame)
            
            # Add new frames with UTF-8 encoding (encoding=3)
            audio.tags.add(COMM(encoding=3, lang='eng', desc='', text=comment_text))
            audio.tags.add(TIT2(encoding=3, text=title_text))
            audio.tags.add(TPE1(encoding=3, text=artist_text))
            audio.tags.add(TCON(encoding=3, text=genre_text))
            audio.tags.add(TXXX(encoding=3, desc='LABEL', text=label_text))
            
            # Save the updated tags back to the file
            audio.save()
            success_count += 1
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
    
    print(f"Total files processed for tags: {success_count}")
    return success_count



#!#!#!#!#! RUNNING STATEMENTS #!#!#!#!#! 
# Example usage:
# Assume df is a pandas DataFrame with columns:
# 'Path', 'comment', 'title', 'artist', 'genre', and 'label'
# For instance:
# df = pd.DataFrame({
#     'Path': ['file1.aiff', 'file2.aiff'],
#     'comment': ['Great sound', 'Live performance'],
#     'title': ['Song One', 'Song Two'],
#     'artist': ['Artist A', 'Artist B'],
#     'genre': ['Rock', 'Jazz'],
#     'label': ['Label1', 'Label2']
# })
#
# Run the function as follows:
# result = _write_2411_i1_SET_id3_tags_bulk(df)
# print(f"Processed {result} files.")

