exec(open("_all_fns_.py",encoding="utf-8").read())
#
#
my_aiff = "/Users/yerik/Music/_1_NEW_SOURCE/_2025_this/test"
##
#

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

###############################################         PREPARE VARIABLES / ausio_extension and loc -> directory variables# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# CHECK THAT AIFF FILES ARE IN CORRECT FORMAT OR REEFORMAT 
#
#results_df = analyze_and_downsize_aiff(my_aiff)
#print(results_df.head())
print('\nALL AIFF in correct format -> if something changes go erase the already downsized\n ')
input('ENTER to analyze \n')
####
##
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

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# COMM ::: _1_ MSG_AUDIO general ATTRIBUTES
#
df = _audio_attr_extract_11_INFO_AIFF(df, audio_extensions)#;input('')

# -----######-----######-----######-----######-----######-----######-----
# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# COMM ::: _2_ LUFS
#
df['ms_lufs'] = compute_lufs_for_paths_AIFF(df['Path'])
df['ms_LUFS_code'] = df['ms_lufs'].apply(_all_values_CREATE_12_LUFS_categories); lufs_cols =['ms_lufs','ms_LUFS_code']
####
##
#

# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# COMM ::: _3_BPM Dynamic vs Normal 
#
# Process the DataFrame with 10% of the track excluded from the start and end:
df = _df_bpm_2409_i1_GET_df_bpm_variation(
    df,
    path_column='Path',
    sr_column='sr',
    exclude_start_pct=0.20,
    exclude_end_pct=0.10
)
#print(df_with_bpm.head())
df = _cat_0204_bpm_consistency_GET_cat(df)
####
##
#

# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# COMM ::: process METADATA : _1_title
#
df = df = _titile_0204_id3_filefallback_GET_df_with_titile(df, 'title', 'TRkw', 'ARkw')
print('DONE with getting 1_title')
print(df['title_file'].value_counts())
####
# if function need to write to IDTAGS
##
#

# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# COMM ::: process METADATA : _2_artist
#
df = df = _artist_0204_id3_filefallback_GET_df_with_artist(df, 'artist', 'ARkw', 'MXkw')
print('DONE with getting 2_artist')
print(df['artist_file'].value_counts())
####
##
#

# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# COMM ::: ::: process METADATA : _3_ LABEL
#
df = _label_0204_id3_filefallback_GET_df_with_LABEL(df, 'LABEL', 'LBkw', 'RYkw')
print('DONE with getting 3_LABEL')
print(df['label_file'].value_counts())
df['LABEL'] = df['LABEL'].str.replace('_', ' ').str.replace(r'^[^a-zA-Z]+', '', regex=True)

####
##
#

# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# COMM ::: ::: process METADATA : _4_ GENRE 
#
df = _genre_0204_id3_filefallback_GET_df_with_genre(df, 'genre', 'GNkw', 'RMkw')
print('DONE with getting 4_genre')
print(df['genre_file'].value_counts())
df['genre'] = df['genre'].str.replace('_', ' ').str.replace(r'^[^a-zA-Z]+', '', regex=True)
####
##
#

# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# COMM ::: _5_ release year 
#
df = _relyear_0204_id3_filefallback_GET_df_with_rel_year(df, 'rel_year', 'YRkw', 'PYkw')
print('DONE with getting 5_release_year')
print(df['rel_year_file'].value_counts())

####
##
#

# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# COMM : _6_ KEY 
#

df = _key_0204_id3_filefallback_GET_df_with_key(df, 'KEY', 'KYkw', 'BPkw')
print('DONE with getting 6_KEY')
print(df['key_file'].value_counts())
df['KEY'] = df['KEY'].str.replace('_', ' ').str.replace(r'^[^a-zA-Z]+', '', regex=True)


####
##
#

# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# COMM : remixer and mix type 
#
df = _mixremix_0204_filename_extract_GET_df_mix_and_remixer(df)
print('DONE with getting 7_mix_name & 8_remixer')
df[['mix_name', 'remixer']].head()
### if you find remix in path = remix = 'r'
from tqdm.auto import tqdm; tqdm.pandas()
df['remix'] = df['Path'].progress_apply(lambda x: 'R' if 'remix' in str(x).lower() else 'U')
#df
####
##
#

# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# COMM : PUrchased date 
#
df = _datepurch_0204_filename_extract_GET_df_with_date_purchased(df)
print('DONE with getting 9_date_purchased')
#df[['temp_id', 'date_purchased']].head()

####
##
#

# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# COMM --------------- >> NOW WRITE TAGS BACK ::: 7_8_ Remixer and mix name to col remixer in REKORBOX
#
df['remixer'] = (df['mix_name'].fillna('') + ' ' + df['remixer'].fillna('')).str.strip()
df['remixer'] = df['remixer'].str.replace('_', ' ').str.replace(r'^[^a-zA-Z]+', '', regex=True)
_aiff_0102_i1_GET_update_remixer_tpe4_tag(df)
print('DONE with WRITTING 7_mix_name & 8_remixer : to ID3TAG remixer')
####
##
#

# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# COMM --------------- >> NOW WRITE GENRE BACK ::: 4_ genre for genre in REKORBOX
#
#!#!#!#!#! RUNNING STATEMENTS #!#!#!#!#!
# To run the function, simply call it on your DataFrame:
processed_count = _write_genre_id3_bulk(df, path_col="Path", genre_col="genre")
print('DONE with WRITTING 4_genre : to ID3TAG genre')

####
##
#

# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# COMM --------------- >> NOW WRITE LABEL BACK ::: 3_ LABEL for label in REKORBOX
#
#!#!#!#!#! RUNNING STATEMENTS #!#!#!#!#!
#To run the function, simply call:
processed_label_count = _write_label_id3_bulk(df, path_col="Path", label_col="LABEL")
print('DONE with WRITTING 3_LABEL : to ID3TAG LABEL')

####
##
#

# -----######-----######-----######-----######-----######-----######-----

############## from here _fns_add
exec(open("_fns_add.py",encoding="utf-8").read())
# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# GET release date 
#
df = _reldate_0204_id3_filefallback_GET_df_with_rel_date(df, 'rel_date', 'RYkw_', '_PYkw')
####
##
# WRITE  release date  to TAGS
_write_reldate_id3_bulk(df, path_col='Path', reldate_col='rel_date')

# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# KEY 
#
df = _key_0403_i2_GET_keys(df)
####
## WRITE KEY to AIFF
#
df = _write_tags_2712_id3_SET_key_bulk(df, "Path", "key_dj")
# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# COMM
#
## re
####
##
#

# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# COMM
#
## re
####
##
#

# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# COMM
#
## re
####
##
#

# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# COMM
#
## re
####
##
#

# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# COMM
#
## re
####
##
#

# -----######-----######-----######-----######-----######-----######-----

