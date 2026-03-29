# =========================================================
# -----######-----  MAIN FUNCTION  -----######-----
# =========================================================

import os
import shutil
from tqdm import tqdm
from pydub import AudioSegment
from mutagen import File
from mutagen.aiff import AIFF

# ---------------------------------------------------------
# FUNCTION
# ---------------------------------------------------------
def _au_2903_i4_GET_df_aiff_FINAL(df, audio_extensions):

    df = df.copy()

    # ---------------------------------
    # INITIAL EXTENSION
    # ---------------------------------
    df['old_Extension'] = df['Path'].apply(lambda x: os.path.splitext(x)[1])
    df['Extension'] = df['old_Extension']

    # ---------------------------------
    # NEW COLS
    # ---------------------------------
    df['status'] = None
    df['error'] = None
    df['sr'] = None
    df['channels'] = None
    df['bit_depth'] = None

    # ---------------------------------
    # LOOP
    # ---------------------------------
    for i in tqdm(range(len(df)), desc='🔥 AIFF FINAL PIPELINE'):

        path = df.loc[i, 'Path']

        try:

            # -----------------------------
            # VALIDATION
            # -----------------------------
            if not os.path.exists(path):
                df.loc[i, 'error'] = 'missing_file'
                continue

            ext = df.loc[i, 'old_Extension']

            if ext not in audio_extensions:
                df.loc[i, 'error'] = 'invalid_ext'
                continue

            base = os.path.splitext(path)[0]
            final_path = base + '.aiff'
            temp_path  = base + '__temp__.aiff'

            # -----------------------------
            # LOAD AUDIO
            # -----------------------------
            audio = AudioSegment.from_file(path)

            # -----------------------------
            # EXTRACT CURRENT INFO
            # -----------------------------
            sr = audio.frame_rate
            ch = audio.channels
            bd = audio.sample_width * 8

            # -----------------------------
            # CHECK PERFECT AIFF
            # -----------------------------
            if ext.lower() in ['.aiff', '.aif'] and sr == 44100 and ch == 2 and bd == 16:
                
                df.loc[i, 'Path'] = path
                df.loc[i, 'Extension'] = '.aiff'
                df.loc[i, 'sr'] = sr
                df.loc[i, 'channels'] = ch
                df.loc[i, 'bit_depth'] = bd
                df.loc[i, 'status'] = 'skipped_perfect'
                continue

            # -----------------------------
            # STANDARDIZE
            # -----------------------------
            audio = audio.set_frame_rate(44100)
            audio = audio.set_sample_width(2)
            audio = audio.set_channels(2)

            # -----------------------------
            # EXPORT (STRICT)
            # -----------------------------
            audio.export(
                temp_path,
                format='aiff',
                parameters=[
                    "-acodec", "pcm_s16be",
                    "-ar", "44100",
                    "-ac", "2"
                ]
            )

            # -----------------------------
            # METADATA COPY
            # -----------------------------
            try:
                src = File(path)
                dst = AIFF(temp_path)

                if src:
                    for k in src.keys():
                        dst[k] = src[k]

                dst.save()
            except:
                pass

            # -----------------------------
            # SAFE MOVE
            # -----------------------------
            shutil.move(temp_path, final_path)

            # -----------------------------
            # DELETE ORIGINAL IF DIFFERENT
            # -----------------------------
            if os.path.abspath(path) != os.path.abspath(final_path):
                try:
                    os.remove(path)
                except:
                    pass

            # -----------------------------
            # UPDATE DF
            # -----------------------------
            df.loc[i, 'Path'] = final_path
            df.loc[i, 'Extension'] = '.aiff'
            df.loc[i, 'sr'] = 44100
            df.loc[i, 'channels'] = 2
            df.loc[i, 'bit_depth'] = 16
            df.loc[i, 'status'] = 'converted'

        except Exception as e:

            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)

            df.loc[i, 'error'] = str(e)
            df.loc[i, 'status'] = 'error'

    return df