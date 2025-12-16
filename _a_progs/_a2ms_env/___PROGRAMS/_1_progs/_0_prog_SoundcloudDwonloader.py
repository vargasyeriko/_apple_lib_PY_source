import os
import sys
from datetime import datetime

# Make sure your global fns folder is visible
sys.path.append("/Users/yerik/_apple_lib/_a_progs/_a2ms_env/___PROGRAMS/_0_fns")

from _0_SoundcloudDwonloader import (
    _soundcloud_1808_pl2name_GET_df,
    _sc_1808_df_GET_audio_for_src_playlist_APPEND,
)


# ==============================
# BASIC CONFIG (EDIT IF NEEDED)
# ==============================
BASE_DOWNLOAD_DIR = "/Users/yerik/Downloads"  # parent folder where everything will be created
EXT     = "mp3"                               # "mp3", "wav", or "aiff"
KBPS    = 320                                 # only used for mp3
COOKIES = None                                # e.g. "/Users/yerik/Downloads/cookies.txt" if needed


def main():
    # ==============================
    # INTERACTIVE INPUTS
    # ==============================

    # 1) Ask for playlist URL
    pl_name = input("\nPaste SoundCloud playlist/SET URL:\n> ").strip().strip('"').strip("'")
    if not pl_name:
        raise ValueError("No playlist URL provided. Exiting.")

    # 2) Ask for a keyword for folder name
    keyword = input("\nKeyword for this download folder (e.g. salsa, halloween, reggaeton):\n> ").strip()
    if not keyword:
        keyword = "soundcloud"

    # make it file-system friendly
    safe_keyword = keyword.replace(" ", "_")

    # 3) Build folder name: mm_dd_keyword_soundcloud_audio
    date_prefix = datetime.now().strftime("%m_%d")
    folder_name = f"{date_prefix}_{safe_keyword}_soundcloud_audio"

    OUT_DIR = os.path.join(BASE_DOWNLOAD_DIR, folder_name)
    os.makedirs(OUT_DIR, exist_ok=True)

    src_folder = OUT_DIR  # keep your original variable name for downstream use (if needed)

    print("\n==============================")
    print(f" Playlist URL : {pl_name}")
    print(f" Output folder: {OUT_DIR}")
    print("==============================\n")

    # ==============================
    # DOWNLOAD TRACKS
    # ==============================

    # If you want genre / purchase_date, add them here:
    # df_tracks = _soundcloud_1808_pl2name_GET_df(pl_name, genre="Salsa", purchase_date="08-18-2025")
    df_tracks = _soundcloud_1808_pl2name_GET_df(pl_name)

    df_tracks = _sc_1808_df_GET_audio_for_src_playlist_APPEND(
        df_tracks,
        out_dir=OUT_DIR,
        ext=EXT,
        prefer_bitrate=KBPS,
        cookies_path=COOKIES,
    )

    # ==============================
    # OPTIONAL: SAVE LOG
    # ==============================
    log_path = os.path.join(OUT_DIR, "_dl_log.csv")
    df_tracks.to_csv(log_path, index=False)

    print(f"\n✅ Done. Download log saved to:\n{log_path}\n")


# ==============================
# ENTRY POINT
# ==============================
if __name__ == "__main__":
    main()
