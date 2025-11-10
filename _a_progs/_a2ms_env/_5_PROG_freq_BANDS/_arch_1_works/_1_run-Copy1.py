#!/usr/bin/env python3
# !#!#!#!#! RUNNING STATEMENTS #!#!#!#!#!
# Minimal launcher for the 3-band Textual console

import os
import sys
import traceback

# ---- Point to your 0_FNS file directory ----
FNS_FILE = "/Users/yerik/_apple_lib/_a_progs/_a2ms_env/_5_PROG_freq_BANDS/_0_fns.py"
FNS_DIR = os.path.dirname(FNS_FILE)

if FNS_DIR and FNS_DIR not in sys.path:
    sys.path.insert(0, FNS_DIR)

try:
    from _0_fns import _audio_0611_textual3band_GET_live_eq_console
except Exception as e:
    print("ERROR: Could not import from _0_fns.py")
    print(f"- Expected location: {FNS_FILE}")
    print("- Check that the file exists and contains the function:")
    print("  _audio_0611_textual3band_GET_live_eq_console()")
    print("\nTraceback:")
    traceback.print_exc()
    sys.exit(1)

def main():
    print("Launching 3-band live EQ console (Textual)...")
    print("Tip: Use your mouse to drag the sliders. Press Ctrl+C to quit.\n")
    _audio_0611_textual3band_GET_live_eq_console()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Bye!")
