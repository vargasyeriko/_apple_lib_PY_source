# ------------------------------------------------------------
# -----######-----  CORE FUNCTION  -----######-----
# ------------------------------------------------------------
def _ms_music_files_export(path_root, audio_extensions):
    import pandas as pd
    import shutil
    import os
    from tqdm import tqdm
    import subprocess
    
    import sys;import io

    import os
    import pandas as pd
    from tqdm import tqdm

    rows = []

    # ---------------------------------
    # WALK DIRECTORY (WITH TQDM)
    # ---------------------------------
    for root, _, files in os.walk(path_root):
        for f in tqdm(files, desc="Scanning files", leave=False):
            
            # skip system junk
            if f.startswith('._') or f.startswith('.DS'):
                continue

            ext = os.path.splitext(f)[1]
            full_path = os.path.join(root, f)

            try:
                size_mb = os.path.getsize(full_path) / (1024 * 1024)
            except:
                size_mb = 0

            rows.append([full_path, f, ext, size_mb])

    # ---------------------------------
    # BUILD DF
    # ---------------------------------
    df = pd.DataFrame(rows, columns=['Path', 'file_name', 'Extension', 'Size (MB)'])

    # ---------------------------------
    # FILTER AUDIO
    # ---------------------------------
    df_AU = df[df['Extension'].isin(audio_extensions)].copy()

    # ---------------------------------
    # FREQUENCY
    # ---------------------------------
    frequency_by_extension = df_AU['Extension'].value_counts().reset_index()
    frequency_by_extension.columns = ['Extension', 'frequency']

    # ---------------------------------
    # SIZE
    # ---------------------------------
    total_size_by_extension = (
        df_AU.groupby('Extension')['Size (MB)']
        .sum()
        .reset_index()
        .rename(columns={'Size (MB)': 'total_size_in_mb'})
    )

    # ---------------------------------
    # MERGE
    # ---------------------------------
    result = pd.merge(frequency_by_extension, total_size_by_extension, on='Extension')

    # ---------------------------------
    # PRINT SUMMARY
    # ---------------------------------
    print('\n\n FREQUENCY TABLE of \n\n', audio_extensions, '\n\n')
    print('total music files : ', result['frequency'].sum(), '\n\n', result)
    print(f'\n ATTN -> \nDF ALL files ::: df :{len(df)}:: & \nDF AUDIO ::: df_AU ::{len(df_AU)}:')

    return df, df_AU, result