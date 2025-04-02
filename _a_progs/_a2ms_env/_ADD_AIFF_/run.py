

exec(open("AIFF_fns.py",encoding="utf-8").read())

final_path = _pathfinder_0104_navigator_GET_final_path()
print("\n📌 Final Selected Path:", final_path)

import pandas as pd

# Adjust settings to display all rows and columns
pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', 1000)  # Set a wide display width to fit the content
pd.set_option('display.max_colwidth', None)  # Show full column content without truncation

#exec(open(f"/Users/yerik/_apple_source/_0_fns_MANAGER.py",encoding="utf-8").read()) # copy_fns()
#%%writefile /Users/yerik/_apple_source/PY/functions/_GLOBAL/_2ms/_song_attr_mapping.py
exec(open("/Users/yerik/_apple_source/pd2.py",encoding="utf-8").read())
#
print(" \n\nget_fns()#;copy_fns()#get_fns() FNS_FNS_FNS") 
#
my_aiff = final_path
#"/Volumes/HD_back_UP/2025_ALL_AIFF_raw/_2023_this/_23_02_AN_LA_VENTANA"
#
import sys;sys.path.append('/Users/yerik/_apple_source/PY/functions/_GLOBAL/_2ms')
#
### ALL AUDIO TYPES ^<<< _***_0_***_ >>>^
#
from df_AIFF_new import compute_lufs_for_paths_AIFF,_audio_attr_extract_11_INFO_AIFF,process_metadata_optimized_AIFF,_df_GET_rework_type_AIFF
#
from df_read import _filefinder_by_EXT_GET_df
#
from _MSG_GET_song_attributes import _audio_attr_all_audio_formats_extract_11_INFO
from _MSG_GET_song_attributes import _all_au_ext_GET_12_LUFS_values,_all_values_CREATE_12_LUFS_categories

#
### MP3 id tags    ^<<< _***_1_***_ >>>^
#
from mp3_tags import process_metadata_optimized_mp3
#
from df_modif import _rename_reorder_GET_df
#
from _song_attributes_mapping import add_country_column_based_on_isrc, _df_GET_mp3_rework_type
from _song_attributes_mapping import extract_and_convert_key,extract_and_convert_key_AIFF ,display_missing_data_by_extension
#
# GENERAL
from tqdm import tqdm


######################
# # Running the function with corrected folder path
results_df = analyze_and_downsize_aiff(my_aiff)

# # Display results
results_df.head()
print('doone')

########################

###############################################         PREPARE VARIABLES / ausio_extension and loc -> directory variables
#
### -------------------------------------------- >>> FILTER by AIFF
code = 'all_AIFF'
audio_extensions = [ '.AIFF', '.aif', '.aiff'];file_extensions = audio_extensions 
# 
my_folder_path = my_aiff
#my_folder_path_mp3 = f'/Users/yerik/Downloads/{folder_name_new}_mp3'
#my_folder_path = {folder_name_new}'
table_name = f"temp_now_{code}.pkl"
#
###############################################          READ by Audio Ext & RETREIVE GENERAL Audio Info 
#^<<< _***_0_***_ >>>^
#
####
### -------------------------------------------- >>> FILTER by AIFF --------- here below ::: audio_extensions
#
df, fre_tab = _filefinder_by_EXT_GET_df(my_folder_path, file_extensions = audio_extensions)#file_extensions = None-> 4 none ext
df = df[~df['Name'].str.startswith('._')].copy();df = df[~df['Name'].str.startswith('.DS')].copy() # omit not wanted
df = df.rename(columns={'Name': 'temp_id'}).drop(columns=['Size (MB)',])                           # KEEP & RENAME
#df = df[df['Extension'].isin(['.mp3', '.MP3'])].copy() # KEEP ONLY extension type 
#
####
#input('')
if not df.empty:
    #
    #_1_ MSG_AUDIO general ATTRIBUTES
    #
    df = _audio_attr_extract_11_INFO_AIFF(df, audio_extensions)#;input('')
    #
    #_2_ MSG_LUFS
    #
    df['ms_lufs'] = compute_lufs_for_paths_AIFF(df['Path'])
    df['ms_LUFS_code'] = df['ms_lufs'].apply(_all_values_CREATE_12_LUFS_categories); lufs_cols =['ms_lufs','ms_LUFS_code']
    #
    #_3_ MSG_BPM
    #
    #df['BPM']
    #
    ## -> KEEP COLS_0 :::
    #
cols_0 = ['temp_id', 'Path', 'Extension', 'dur_seconds', 'dur_min', 'sr', 'bit_rate', 'bit_depth', 
              'channels', 'file_size', 'file_size_human', 'num_frames', 'error']  + lufs_cols
###
###############################################            RETREIVE       MP3 ID TAGS
#^<<< _***_1_***_ >>>^
#
#input('')
if not df.empty:
    df = process_metadata_optimized_AIFF(df, file_column='Path');print('DONE with getting ID3 tags')

    df = _rename_reorder_GET_df(df);print('DONE with renaming ID3 tags')
    df = process_date_column(df);print('DONE with processing ID3 tags for DATES');df['isrc'] = ''
    df = add_country_column_based_on_isrc(df);print('DONE with processing ID3 tags for isrc rel_COUNTRY_code')
    df =  _df_GET_rework_type_AIFF(df, col='Path');print('DONE with processing ID3 tags for REWORK type')
    df['KEY'] = '';df['BPM'] = '';df['LABEL'] = ''
    df = extract_and_convert_key_AIFF(df);print('DONE with conversion Camelot ID3 KEYS')
    #
    ## -> KEEP COLS_1 :::
    #
    cols_1 = [ 'title','artist','rework','album','track_#','genre','LABEL','isrc','rel_country',
               'rel_date',  'year','rel_year', 'rel_month', 'rel_day', 'rel_weekday',
               'audio_offset', 'decoder','comment','BPM', 'KEY', 'KEYC', 'KEY_code' ]     


# after id3 TAG abstractions
df = df[cols_0 + cols_1];
display_missing_data_by_extension(df)
print('done')#display Freq table of attributes by extension and list of vars