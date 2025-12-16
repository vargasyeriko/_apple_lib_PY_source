import sys
import os

# add fns directory to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FNS_DIR  = os.path.join(BASE_DIR, "_0_fns")
sys.path.append(FNS_DIR)

from _1_fn_check_mp3s import _mp3norm_0812_safe_GET_report_delete

print("\n=== SAFE MP3 NORMALIZER + SHORT FILE CLEANER ===")
print("This will:")
print("  1) Ask you for the folder containing .mp3")
print("  2) Normalize safely (never clipping)")
print("  3) Report files < 2.5 min")
print("  4) Delete them after you hit ENTER\n")

folder = input("Enter folder path where MP3 files are located:\n> ").strip()

if not folder:
    print("\n[ERR] No folder entered. Exiting.")
else:
    _mp3norm_0812_safe_GET_report_delete(
        folder_path=folder,
        target_dbfs=-1.0,
        min_duration_sec=150,
        export_bitrate="320k"
    )
