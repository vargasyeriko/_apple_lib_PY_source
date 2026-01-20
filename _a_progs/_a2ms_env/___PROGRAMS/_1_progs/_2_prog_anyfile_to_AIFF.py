# ----------------------------######----------------------------#
#   _2_prog_anyfile_to_AIFF                                   #
# ----------------------------######----------------------------#

import os
import sys
import pandas as pd

# make sure we can import from your functions folder
sys.path.append("/Users/yerik/_apple_lib/_a_progs/_a2ms_env/___PROGRAMS/_0_fns")

from _2_fn_anyfile_to_AIFF import _aiff_0109_all2aiff_GET_summary
from _2_fn_anyfile_to_AIFF import _cleanup_2208_keepaiff_GET_removed_files
from _2_fn_anyfile_to_AIFF import _id3_1901_kwname_GET_df_ready


def main():
    print("!!! --- > THIS fn takes any audio file to AIFF, even AIFF files gets converted to desire format, and renames !!!")
    print("!!! --- > FOR custom tags i.e. name, release year etc go inside prog  !!!")

    # --------- REQUIRED ---------
    root_folder = input("📁 root_folder (folder to scan):\n> ").strip().strip('"').strip("'")
    root_folder = os.path.expanduser(root_folder)

    # --------- OPTIONAL (Enter => None) ---------
    out_root = input("📁 out_root (press Enter = None):\n> ").strip().strip('"').strip("'")
    out_root = os.path.expanduser(out_root) if out_root else None

    # Externalized extensions (case-insensitive auto-handled inside fn)
    audio_extensions = [".flac", ".wav", ".mp3", ".aiff", ".aif", ".m4a", ".aac", ".alac", ".ogg", ".oga", ".wv", ".aifc"]

    # Action knobs
    dry_run    = "n"           # "y" to preview only
    overwrite  = "y"           # "y" to force re-encode even if dst exists
    src_action = "keep"        # "keep" | "move" | "trash"
    move_dir   = "/Users/yerik/Desktop/_SRC_MOVED"  # required if src_action=="move"

    summary = _aiff_0109_all2aiff_GET_summary(
        root_folder=root_folder,
        out_root=out_root,
        audio_extensions=audio_extensions,
        dry_run=dry_run,
        src_action=src_action,
        src_action_move_dir=move_dir,
        overwrite=overwrite
    )

    input("\n✅ DONE converting files , press enter to erase original ones after checking !!! \n")

    ## ERASE files 
    _cleanup_2208_keepaiff_GET_removed_files(root_folder, dry_run="n")

    ### get DF 
    
        # ----------------------------######----------------------------#
    #   #!#!#!#!#! RUNNING STATEMENTS #!#!#!#!#!                   #
    # ----------------------------######----------------------------#
    
    # ==========================
    # REQUIRED
    # ==========================
    root_folder =root_folder  # <-- change this
    
    # ==========================
    # OPTIONAL OVERRIDES
    # Leave "" to use AIFF tags (or filename fallback for title)
    # ==========================
    custom_artist        = ""          # e.g. "YerikoDJ"
    custom_genre         = ""          # e.g. "Detroit_House"
    custom_label         = ""          # e.g. "Metroplex"
    custom_release_date  = ""          # e.g. "2025_08_15"  (if blank, uses TDRC if present else NA)
    custom_purchase_date = ""          # e.g. "2026_01_19"  (if blank, becomes NA)
    
    # ==========================
    # SCAN SETTINGS
    # ==========================
    audio_extensions   = (".aiff", ".aif")
    include_subfolders = "y"
    
    df = _id3_1901_kwname_GET_df_ready(
        root_folder=root_folder,
        custom_artist=custom_artist,
        custom_genre=custom_genre,
        custom_label=custom_label,
        custom_release_date=custom_release_date,
        custom_purchase_date=custom_purchase_date,
        audio_extensions=audio_extensions,
        include_subfolders=include_subfolders
    )
    pd.set_option("display.max_colwidth", None)
    for i, r in enumerate(df["new_name"], start=1):
        print(f"{i:03d} → {r}")
    return summary

    
