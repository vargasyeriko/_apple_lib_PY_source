# =========================================================
# -----######-----  MAIN FUNCTION  -----######-----
# =========================================================

import os
import pandas as pd
from tqdm import tqdm
from datetime import datetime
import re

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def _clean_text(x):
    if pd.isna(x):
        return ''
    x = str(x)
    x = re.sub(r'[\\/*?:"<>|]', '', x)
    x = re.sub(r'\s+', '_', x.strip())
    return x

def _parse_date(val):
    if pd.isna(val):
        return ('', '', '')

    val = str(val)

    if re.fullmatch(r'\d{4}', val):
        return (val, '', '')

    try:
        dt = pd.to_datetime(val, errors='coerce')
        if pd.notna(dt):
            return (str(dt.year), f"{dt.month:02d}", f"{dt.day:02d}")
    except:
        pass

    return ('', '', '')

# ---------------------------------------------------------
# FUNCTION
# ---------------------------------------------------------
def _rename_2903_i2_GET_df_confirm(df):

    df = df.copy()

    today = datetime.today()
    py, pm, pd_ = str(today.year), f"{today.month:02d}", f"{today.day:02d}"

    df['Path_new'] = None
    df['Name'] = None

    # ---------------------------------
    # BUILD ALL NAMES FIRST
    # ---------------------------------
    for i in range(len(df)):

        path = df.loc[i, 'Path']
        ext = os.path.splitext(path)[1]

        # TITLE / ARTIST
        title = df.loc[i, 'idt_title'] if 'idt_title' in df.columns else None
        artist = df.loc[i, 'idt_artist'] if 'idt_artist' in df.columns else None

        if pd.isna(title) or title is None:
            title = os.path.splitext(os.path.basename(path))[0]

        title = _clean_text(title)
        artist = _clean_text(artist)

        # GENRE
        genre = ''
        if 'idt_genre' in df.columns and pd.notna(df.loc[i, 'idt_genre']):
            genre = _clean_text(df.loc[i, 'idt_genre'])

        # RELEASE DATE
        ry, rm, rd = ('', '', '')
        if 'idt_year' in df.columns:
            ry, rm, rd = _parse_date(df.loc[i, 'idt_year'])

        # BUILD NAME
        new_name = (
            f"TRkw_{title}_"
            f"ARkw_{artist}_"
            f"MXkw__KYkw__BPkw__"
            f"GNkw_{genre}_"
            f"RMkw__LBkw__"
            f"RYkw_{ry}_{rm}_{rd}_"
            f"PYkw_{py}_{pm}_{pd_}"
            f"{ext}"
        )

        new_path = os.path.join(os.path.dirname(path), new_name)

        df.loc[i, 'Path_new'] = new_path
        df.loc[i, 'Name'] = os.path.splitext(new_name)[0]

    # ---------------------------------
    # PREVIEW TABLE
    # ---------------------------------
    preview = df[['Path', 'Path_new', 'Name']]

    print("\n========== RENAME PREVIEW ==========\n")
    print(preview.to_string(index=False))

    # ---------------------------------
    # CONFIRMATION
    # ---------------------------------
    confirm = input("\nProceed with renaming? (y/n): ").strip().lower()

    if confirm != 'y':
        print("\n❌ Renaming cancelled.")
        return df

    # ---------------------------------
    # EXECUTE RENAME
    # ---------------------------------
    df['rename_status'] = None
    df['error'] = None

    for i in tqdm(range(len(df)), desc='✏️ Renaming files'):

        try:
            old_path = df.loc[i, 'Path']
            new_path = df.loc[i, 'Path_new']

            if not os.path.exists(old_path):
                df.loc[i, 'error'] = 'missing_file'
                continue

            os.rename(old_path, new_path)

            df.loc[i, 'Path'] = new_path
            df.loc[i, 'rename_status'] = 'renamed'

        except Exception as e:
            df.loc[i, 'error'] = str(e)
            df.loc[i, 'rename_status'] = 'error'

    return df