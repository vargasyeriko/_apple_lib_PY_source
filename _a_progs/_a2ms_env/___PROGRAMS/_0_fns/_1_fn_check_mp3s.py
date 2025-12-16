import os
from pydub import AudioSegment

# -----######-----######-----######-----######-----
#      SAFE MP3 NORMALIZER + SHORT-FILE DELETER
# -----######-----######-----######-----######-----

def _mp3norm_0812_safe_GET_report_delete(folder_path,
                                         target_dbfs=-1.0,
                                         min_duration_sec=150,
                                         export_bitrate="320k"):
    """
    folder_path      : folder with .mp3 files
    target_dbfs      : safe-peak target (attenuation only)
    min_duration_sec : threshold for deletion (default 2.5 min)
    export_bitrate   : bitrate for exported mp3s
    """

    folder_path = os.path.abspath(folder_path)
    if not os.path.isdir(folder_path):
        print(f"\n[ERR] Folder not found:\n  {folder_path}")
        return

    mp3_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith(".mp3")
    ]

    if not mp3_files:
        print(f"\n[INFO] No mp3 files found in:\n  {folder_path}")
        return

    print(f"\n[INFO] Found {len(mp3_files)} mp3 file(s) in:\n  {folder_path}\n")

    short_files = []

    for idx, fpath in enumerate(sorted(mp3_files), start=1):
        fname = os.path.basename(fpath)
        print(f"[{idx}/{len(mp3_files)}] Processing: {fname}")

        try:
            audio = AudioSegment.from_mp3(fpath)
            duration_sec = len(audio) / 1000.0

            if duration_sec < min_duration_sec:
                short_files.append((fpath, duration_sec))

            # current peak
            max_dbfs = audio.max_dBFS

            # skip silent files
            if max_dbfs == float("-inf"):
                print("   - Silent file detected; skipping normalization.")
                continue

            # only attenuate
            if max_dbfs > target_dbfs:
                gain_db = target_dbfs - max_dbfs  # negative value
                print(f"   - Peak {max_dbfs:.2f} dBFS → applying {gain_db:.2f} dB")
                audio_norm = audio.apply_gain(gain_db)

                temp_out = fpath + ".tmp.mp3"
                audio_norm.export(temp_out, format="mp3", bitrate=export_bitrate)
                os.replace(temp_out, fpath)
            else:
                print(f"   - Peak {max_dbfs:.2f} dBFS → OK (no attenuation)")

        except Exception as e:
            print(f"   [ERR] Failed: {fname} → {e}")

    # REPORT SHORT FILES
    print("\n" + "-"*60)
    print(f"[REPORT] Files shorter than {min_duration_sec/60:.2f} minutes:")

    if not short_files:
        print("  - None (no files will be deleted).")
        return

    for i, (fpath, dur) in enumerate(short_files, start=1):
        m = int(dur // 60)
        s = int(dur % 60)
        print(f"  {i:02d}. {os.path.basename(fpath)}  ({m:02d}:{s:02d})")

    print(f"\n[INFO] Total short files: {len(short_files)}")

    # CONFIRM DELETE
    input("\nPress ENTER to DELETE these files permanently "
          "(Ctrl+C to cancel)...")

    for fpath, _ in short_files:
        try:
            os.remove(fpath)
            print(f"  [DEL] {os.path.basename(fpath)}")
        except Exception as e:
            print(f"  [ERR] Could not delete {os.path.basename(fpath)}: {e}")

    print("\n[DONE] Finished cleanup.")
