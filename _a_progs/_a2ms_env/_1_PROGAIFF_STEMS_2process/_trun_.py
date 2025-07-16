
exec(open("_all_fns_.py",encoding="utf-8").read())

folder_in = folder_input 
# Make sure tqdm is installed first:
# pip install tqdm

_convert_1010_aiff2mp3mono_GET_clean_folder(folder_in)


df = _path_1607_i2_GET_mp3(df)
##### get metadata from name -?>> should re do this step later 
df = _meta_1110_bpm_dur_GET_dominantbpm_and_durmin(df)
print(df.head(10))
print(df['Path'].apply(lambda x: os.path.splitext(x)[1].lower()).value_counts())


print("🎯 Missing BPM values:", df['dominant_bpm'].isna().sum())


df['dominant_bpm'] = df['dominant_bpm'].fillna(120)
print("✅ Filled missing BPM values with 120.")


print("🎯 Missing BPM values:", df['dominant_bpm'].isna().sum())
input('')
# ----------------------------######----------------------------#
#               Run sample chopper on your df                  #
# ----------------------------######----------------------------#

_slice_1110_bars_GET_clean_chunks(
    df=df,
    rms_thresh=-40  # dB threshold to exclude silent/unusable
)


## cover images 

updated_files = _id3_1010_coverembed_GET_df_folder_updatedfiles(df)


root = folder_input 
folders = _list_1107_foldersonly_GET_fullpaths_recursively(root)

len(folders)


# GET sample keys and rename .


df_keys = _key_1110_mp3folders_GET_3topkeys_dj_and_music(folders)

# To preview
print(df_keys[['Path', 'KEY_1', 'KEY_2', 'KEY_3', 'key_dj_1', 'key_dj_2', 'key_dj_3']].head())


df_bu = df_keys

print(len(df_keys))

df_keys = _key_1110_dfkeys_RENAME_by_top3keys_and_clean_filename(df_keys)
