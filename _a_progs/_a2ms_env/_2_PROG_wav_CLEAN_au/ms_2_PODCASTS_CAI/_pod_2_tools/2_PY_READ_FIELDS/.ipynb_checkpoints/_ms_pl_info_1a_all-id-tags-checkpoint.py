

# id tags AIF
df_aif = df[df['Extension'].isin(['.AIFF', '.aiff','.aif','.AIF'])].copy()
if not df_aif.empty:
    exec(open(f"{direc}/_ms_pl_info_1_AIF_IDtags.py",encoding="utf-8").read())
    df_aif = process_metadata_optimized(df_aif, file_column='Path')
    #df_aif['idt_genre'].isnull().sum()


# id tags WAV
df_wav = df[df['Extension'].isin(['.wav', '.WAV'])].copy()
if not df_wav.empty:
    exec(open(f"{direc}/_ms_pl_info_1_WAV_IDtags.py",encoding="utf-8").read())
    df_wav = process_metadata_optimized_wav(df_wav, file_column='Path')
    #df_wav['idt_genre'].isnull().sum()


# id tags mp3
df_mp3 = df[df['Extension'].isin(['.mp3', '.MP3'])].copy()
if not df_mp3.empty:
    exec(open(f"{direc}/_ms_pl_info_1_MP3_IDtags.py",encoding="utf-8").read())
    df_mp3 = process_metadata_optimized_mp3(df_mp3, file_column='Path')
    #df_mp3['idt_genre'].isnull().sum()


# id tags flac
df_flac = df[df['Extension'].isin(['.flac', '.FLAC'])].copy()
if not df_flac.empty:
    exec(open(f"{direc}/_ms_pl_info_1_FLAC_IDtags.py",encoding="utf-8").read())
    df_flac = process_metadata_optimized_flac(df_flac, file_column='Path')
    #df_flac['idt_genre'].isnull().sum()


# id tags m4a
df_m4a = df[df['Extension'].isin(['.m4a', '.M4a'])].copy()
if not df_m4a.empty:
    exec(open(f"{direc}/_ms_pl_info_1_M4A_IDtags.py",encoding="utf-8").read())
    df_m4a = process_metadata_optimized_m4a(df_m4a, file_column='Path')
    #df_m4a['idt_genre'].isnull().sum()

    
columns = ['Name','file_id','Type','Extension','Size (MB)','bitrate','Duration','duration_minutes','Path',
 'idt_title','idt_artist','idt_album','idt_year','idt_track','idt_genre','idt_comment','idt_audio_offset']

# Function to select columns
def select_columns(df, columns):
    # Keep only the columns that exist in the dataframe
    selected_columns = [col for col in columns if col in df.columns]
    return df[selected_columns]

# Specify the columns you want from each data frame
columns_to_pick =columns  # Modify this list based on the columns you want

df_aif = select_columns(df_aif, columns_to_pick)
df_flac = select_columns(df_flac, columns_to_pick)
df_wav = select_columns(df_wav, columns_to_pick)
df_mp3 = select_columns(df_mp3, columns_to_pick)
df_m4a = select_columns(df_m4a, columns_to_pick)

# Concatenate the data frames
dfs_to_concat = [df for df in [df_aif, df_flac, df_wav, df_mp3, df_m4a] if not df.empty]
df = pd.concat(dfs_to_concat, ignore_index=True).copy()






























