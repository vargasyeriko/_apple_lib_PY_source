
####### here TO ADD
# program that smartly renames , from an inbox folder, ask for the name of the folder , and rename ....

# -----######-----######-----######-----######-----######-----#
# FUNCTION: _fs_1704_listsubdirs_GET_list_all
# -----######-----######-----######-----######-----######-----#

import os
from tqdm import tqdm

def _fs_1704_listsubdirs_GET_list_all(root_folder):
    """
    Returns a list of full paths to all immediate subfolders inside the given folder.
    
    Parameters:
        root_folder (str): Path to the root directory

    Returns:
        List of full paths to subdirectories only
    """
    print(f"🔍 Scanning for subfolders in:\n{root_folder}")
    subfolders = [
        os.path.join(root_folder, d)
        for d in os.listdir(root_folder)
        if os.path.isdir(os.path.join(root_folder, d))
    ]
    print(f"✅ Found {len(subfolders)} subfolders.")
    return subfolders
folder_list_23 = _fs_1704_listsubdirs_GET_list_all("/Users/yerik/Music/_1_NEW_SOURCE/_2023_this")
folder_list_24 = _fs_1704_listsubdirs_GET_list_all("/Users/yerik/Music/_1_NEW_SOURCE/_2024_this")
folder_list_25 = _fs_1704_listsubdirs_GET_list_all("/Users/yerik/Music/_1_NEW_SOURCE/_2025_this")


folder_list = folder_list_23 + folder_list_24 + folder_list_25
#print(folder_list)
print('\n\n TOTAL FOLDERS IN TRACKS DB ::: ',len(folder_list), '\n')
### check folders to se ethe ones that already are done 
# -----######-----###### FILTER FOLDERS: EXCLUDE IF 'dylu' FILES EXIST -----######-----######
import os

def _filterfolders_1105_excldylu_GET_cleanlist(folder_list):
    """
    Filters out folders that contain any file starting with 'dylu'.
    Removes duplicates while preserving original order.
    
    Parameters:
    - folder_list: list of folder paths (strings)
    
    Returns:
    - list of unique, valid folders excluding any with 'dylu' files
    """
    seen = set()
    clean_folders = []

    for folder in folder_list:
        if folder in seen:
            continue
        seen.add(folder)

        try:
            if not os.path.isdir(folder):
                continue

            if any(fname.startswith('dylu') for fname in os.listdir(folder)):
                continue

            clean_folders.append(folder)

        except Exception as e:
            print(f"❌ Error in {folder}: {e}")
            continue

    return clean_folders


folder_list = _filterfolders_1105_excldylu_GET_cleanlist(folder_list)

print(folder_list)
input(f'\n\n TO ANALLIZE songs in folders above total of <<< {len(folder_list)}  >>> Enter to continue ! \n\n')
#################

import shutil, os
import pandas as pd
from pathlib import Path

# ───── VOCALS ─────
taken_acronym = input('what is 4 CHARACTER df key word acronym \n\n')
acronym = 't'
folder_list = folder_list 
counter = 0
dfs = []

for path in folder_list:
    try:
        print(f"\n🔁 Processing: {path}")
        my_aiff = path
        direc_jpg = "images/"
        direc_tables = "tables/"
        silence_id = counter + 1
        print(f"📎 Assigned Silence ID = {silence_id}")
        exec(open("run.py", encoding="utf-8").read())

        pkl_name = f"df_{counter:03d}_.pkl"
        df.to_pickle(pkl_name)
        dfs.append(df)
        print(f"✅ Saved: {pkl_name}")
        [shutil.rmtree(f, ignore_errors=True) or os.makedirs(f, exist_ok=True) for f in [direc_jpg, direc_tables]]
        print('images and tables folders erased')
        counter += 1

    except Exception as e:
        print(f"❌ Error in {path}: {e}")
        continue

# ───── CONCAT VOCALS TABLES ─────
final_df = pd.concat(dfs, ignore_index=True)
final_path = f"df_{taken_acronym}{acronym}_final.pkl"
final_df.to_pickle(final_path)
print(f"\n📦 Final vocals DF saved as: {final_path}")

# ───── DELETE TEMP PICKLES ─────
for i in range(counter):
    f = Path(f"df_{i:03d}_.pkl")
    if f.exists():
        f.unlink()
print("🗑️ Temp pickle files deleted.")

# ───── CLEAN MEMORY ─────
del df
dfs = []