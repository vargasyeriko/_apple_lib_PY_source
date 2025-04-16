exec(open("_all_fns_.py",encoding="utf-8").read())
#
#
#my_aiff ="/Volumes/MUSIC_PROD/_1_NEW_SOURCE copy"# 
#my_aiff ="/Users/yerik/Music/_1_NEW_SOURCE/_2025_this/cover"
##
#

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

###############################################         PREPARE VARIABLES / ausio_extension and loc -> directory variables# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# CHECK THAT AIFF FILES ARE IN CORRECT FORMAT OR REEFORMAT 
#
results_df = analyze_and_downsize_aiff(my_aiff)
print(results_df.head())
#input('')
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
df = df[df['Extension'].isin(['.aiff', '.AIFF'])].copy() # KEEP ONLY extension type 

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
df = _lufs_1004_i1_GET_df_id_cat_lufs(df)
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
df =  _title_0204_id3_filefallback_GET_df_with_title(df, 'title', 'TRkw', 'ARkw')
print('DONE with getting 1_title')
print(df['title_file'].value_counts())
####
### get rid of weird characters 
df = _col_2409_txt_clean_single_GET_df(df, 'title')
# if function need to write to IDTAGS
##
_write_title_id3_bulk(df)

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
### get rid of weird characters 
df = _col_2409_txt_clean_single_GET_df(df, 'artist')
# if function need to write to IDTAGS
##
_write_artist_id3_bulk(df)
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
#
#
# -----######-----######-----######-----######-----######-----######-----

############## from here _fns_add
#exec(open("_fns_key.py",encoding="utf-8").read())
# -----######-----######-----######-----######-----######-----######-----

df = _key_bulk_0815_librosa_middle_aiff_GET_output(df)
df = _key_0403_i2_GET_keys(df) # get key_dj and key_music
df = _write_tags_2712_id3_SET_key_bulk(df, "Path", "key_dj") # set to id3 tag
df = _mix_0804_i1_GET_df_5cols(df) # gets jaws key up etc 

# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
df['ID'] = ('dy' + df['bpm_consistency_cat'].str[2] 
            + df['ms_LUFS_code'].str[2].str.upper() 
            + df['id_cat_lufs'].str.lower() +'_'
            + df['title'].str[0].str.lower()
            + df['artist'].str[0].str.upper()
            + df['file_size'].astype(str).str[:2])


df['ms_lufs']
df.sort_values(by='ID')
# 
# COMM
#
## re
df['comment'] = df['ID'] +'_'+ df['KEY'] 
_write_comment_id3_bulk(df) # write comment to id3 tags
####
## CHECK POINT
#

# -----######-----######-----######-----######-----######-----######-----
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random, string


exec(open("cover_fns.py",encoding="utf-8").read())

# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 

###### create KEY plot chamelot map 
key_plot()
#!#!#!#!#! RUNNING STATEMENTS #!#!#!#!#!
# Minimal execution code: Set the directory with your PNG images and call the function.
input_directory = direc_jpg
output_folder = direc_jpg# Directory containing the PNG images that need processing

# Call the function to process and overwrite the images in the same folder.
_png_2409_wbrem_GET_overwrite_imgs(input_directory, tolerance=200)
# Example: Calling the iteration function
_aiff_2409_coveriter_GET_save(df, output_folder, default_pic=None)
# # Example: Calling the iteration function
_aiff_2409_coveriter_GET_save(df, output_folder, default_pic=None)
# # Example: Calling the iteration function
_aiff_2409_coveriter_GET_save(df, output_folder, default_pic=None) # three times to make picture small




# create new IDs
df['Path_jpg_album'] = f'{direc_jpg}' + 'cover_1_' + df['ID'] + '.jpg'
df['Path_jpg_key'] = f'{direc_jpg}' + 'key_plot' + df['ID'] + '.png'

###########################
#!#!#!#!#! RUNNING STATEMENTS #!#!#!#!#!


# Use the 'dominant_bpm' column for the text overlay:
_img_2409_process_df_coverart_GET_output(
    df,
    circle_size_ratio=0.25,         # Increase the size of the circle relative to the image size
    position="top-left",         # Change the position of the circle
    circle_color=(0, 0, 0, 255),    # Use a red circle
    text_color=(0, 255, 25, 255),      # Use a green color for the text
    text_scale=0.5,                 # Adjust the text scale
    text_column="dominant_bpm"      # Use the dominant BPM as text
)

# Example using a different column (e.g., 'artist_name'):
# _img_2409_process_df_coverart_GET_output(
#     df,
#     circle_size_ratio=0.25,
#     position="bottom-left",
#     circle_color=(255, 0, 0, 255),
#     text_color=(0, 255, 0, 255),
#     text_scale=0.7,
#     text_column="artist_name"      # Now the overlay will show the artist name
# )



#Example with no text overlay:
_img_2409_process_df_coverart_GET_output(
    df,
    circle_size_ratio=0.33,
    position="top-right",
    circle_color=(255, 255, 255, 255),
    text_color=(0, 255, 25, 255),
    text_scale=0.5,
    text_column=None               # Passing None will result in no text being drawn
)

#!#!#!#!#! RUNNING STATEMENTS #!#!#!#!#! FOR KEY overly 


# Process each row in the DataFrame by overlaying the key image onto the album cover.
_img_2409_overlay_df_key_GET_output(
    df,
    resize_factor=0.265,         # Adjust as needed to scale the overlay image
    position_right_cm=-0.232,    # Distance from the right edge in cm
    position_top_cm=-0.59,       # Distance from the top edge in cm
    dpi=300                      # DPI used for conversion from cm to pixels
)


# Process the DataFrame: for each row, the overlay function uses the LUFS code from 'ms_LUFS_code'
_overlay_df_circle_custom_0501_GET_image(
    df,
    circle_position=(-0.379, -1.2098003),  # Custom fractional position
    circle_diameter=2755,                  # Custom circle diameter in pixels
    ms_LUFS_column='ms_LUFS_code'           # Column from which to take the LUFS code
)

########### cliping graph 
_audio_2409_i2_GET_generate_clipping_plots(df,save_directory="images")
df['Path_jpg_clip'] = f'{direc_jpg}' + 'clip_plot' + df['ID'] + '.jpg'

# embed freq to pic 
_img_2409_i3_GET_embed_clipping_on_album(df)
####
##
#

# -----######-----######-----DYNAMIC BPM
exec(open("cover_fns_2.py",encoding="utf-8").read())

# -----######-----######-----######-----######-----######-----######-----
# ###########################################################################
# ########## END OF CORE FUNCTION ###########################################
_bpm_2610_i3_GET_partialdonut_bpmdynamic(df, save_dir="images")
df['Path_png_bar_dyn'] = f'{direc_jpg}' + 'bpm_bar_dyn_' + df['ID'] + '.png'
#!#!#!#!#! RUNNING STATEMENTS #!#!#!#!#!
# With your DataFrame 'df' (which contains 'ID', 'Path_png_bar_dyn', and 'Path_jpg_album'),
# call the function to overlay the dynamic PNG onto the album JPG.
_bpm_2610_i4_GET_embedded_album_dynamic_custom(
    df,
    position="top_left",  # adjust as needed: "top_left", "top_right", "bottom_left", "bottom_right", "custom"
    x_offset=3,          # horizontal offset: increase to move right (for top_left or bottom_left) or left (for top_right or bottom_right)
    y_offset=33,          # vertical offset: increase to move down (for top positions) or up (for bottom positions)
    scale=.65             # adjust the scale if needed
    # custom_coords=(x, y) can be provided if position is "custom"
)

# embed freq to pic 
#_img_2409_i3_GET_embed_clipping_on_album(df)
# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# LUFS second graph 
####
##
#

_lufs_1504_i1_GET_partialdonut_lufs(df, save_dir="images/")
df['Path_png_bar_lufs'] = f'{direc_jpg}' + 'lufs_bar_dyn_' + df['ID'] + '.png'

_lufs_1504_i2_GET_embedded_album_lufs_custom(
        df,
    position="top_left",  # adjust as needed: "top_left", "top_right", "bottom_left", "bottom_right", "custom"
    x_offset=-19,          # horizontal offset: increase to move right (for top_left or bottom_left) or left (for top_right or bottom_right)
    y_offset=8,          # vertical offset: increase to move down (for top positions) or up (for bottom positions)
    scale=.75             # adjust the scale if needed
    # custom_coords=(x, y) can be provided if position is "custom"
)
# THIS FUNCTION CHANGES the column ms LUFS code

# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 

####TEXTURE AND SHAPE 
##
#
df = _spectral_1604_sf_i1_GET_df_feats(df)
# create plot for texture and shape
_text_shape_1604_i1_GET_rectbar_centroidcolor(df, save_dir="images/")

# EMBED 

_text_shape_1604_i2_GET_embedded_album_text_shape_custom(
    df,
    position="bottom_left",
    x_offset=1,
    y_offset=417,
    scale=3
)
_text_shape_1604_i2_GET_embedded_album_text_shape_custom(
    df,
    position="bottom_left",
    x_offset=1,
    y_offset=981,
    scale=3
)

_text_shape_1604_i2_GET_embedded_album_text_shape_custom(
    df,
    position="bottom_left",
    x_offset=981,
    y_offset=630,
    scale=5
)


_text_shape_1604_i2_GET_embedded_album_text_shape_custom(
    df,
    position="bottom_left",
    x_offset=-2308,
    y_offset=630,
    scale=5
)
# -----######-----######-----######-----######-----######-----######-----
df = _aiffspec_1504_i3_GET_df_spectralcolorcode(df)
_centroid_1604_i2_GET_donutfade_centroidcolor(df, save_dir="images/")

# -----######-----######-----######-----######-----######-----######-----

_centroid_1604_i3_GET_embedded_album_centroid_custom(
    df,
    position="top_right",
    x_offset=-28,
    y_offset=-61,
    scale=3
)
# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
#_aiff_2409_i1_GET_embed_aiff_covers(df)
####
##
#

# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 

####
##
#

# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# RENAME

## re
# df['re_name'] = ( df['ID'] +'_'
#                  +'BY_'+ df['artist'].astype(str).str[:5]
#                  +'_'+df['title'].astype(str).str[:9]
#                  +'_'+ df['remix'].astype(str))
# ####
# ##
# #
# _rename_aiff_files_bulk(df)
# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# COMM
# Assume 'df' is your DataFrame and you have a list of column names to clean, e.g.:
# list_of_columns = ['column1', 'column2', 'column3']
#
# To perform the cleaning, simply call:
# cleaned_df = _col_2409_txt_clean_GET_df(df, list_of_columns)
#

# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 
# COMM
df = _hash_bulk_2812_audio_GET_df_hashes(df)
print("DOoooooooooooo\n\n\n\n\n\n\nne...")
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

