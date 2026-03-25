#!/usr/bin/env python3

# ==========================================================
# MACOS FULL CACHE CLEANER
# Cleans browser, WebKit, GPT storage, Office, logs, shells
# Then optionally restarts system
# ==========================================================

import os
import shutil
import subprocess
from pathlib import Path
import time

# ----------------------------------------------------------
# Helper functions
# ----------------------------------------------------------

def delete_item(path):

    try:
        if path.is_file() or path.is_symlink():
            path.unlink()
            print(f"removed file: {path}")

        elif path.is_dir():
            shutil.rmtree(path)
            print(f"removed directory: {path}")

    except Exception as e:
        print(f"skipped {path} ({e})")


def clean_folder(folder):

    folder = Path(folder).expanduser()

    if not folder.exists():
        return

    for item in folder.iterdir():
        delete_item(item)


def run_cmd(cmd):

    try:
        subprocess.run(cmd, shell=True)
    except Exception as e:
        print("command failed:", e)


# ----------------------------------------------------------
# Kill browsers to avoid corruption
# ----------------------------------------------------------

print("\nClosing browsers...\n")

run_cmd("killall Safari 2>/dev/null")
run_cmd("killall Google\\ Chrome 2>/dev/null")
run_cmd("killall Firefox 2>/dev/null")

time.sleep(2)

# ----------------------------------------------------------
# Cache locations
# ----------------------------------------------------------

locations = [

    # macOS user caches
    "~/Library/Caches",

    # Safari + WebKit (ChatGPT uses this heavily)
    "~/Library/WebKit",
    "~/Library/Safari/LocalStorage",
    "~/Library/Safari/Databases",

    # Chrome
    "~/Library/Application Support/Google/Chrome/Default/Cache",
    "~/Library/Application Support/Google/Chrome/Default/Code Cache",
    "~/Library/Application Support/Google/Chrome/Default/GPUCache",

    # Firefox
    "~/Library/Application Support/Firefox/Profiles",

    # Office
    "~/Library/Containers/com.microsoft.Word/Data/Library/Caches",
    "~/Library/Containers/com.microsoft.Excel/Data/Library/Caches",
    "~/Library/Containers/com.microsoft.Powerpoint/Data/Library/Caches",

    # Logs
    "~/Library/Logs",

    # Crash reports
    "~/Library/Application Support/CrashReporter",

    # terminal sessions
    "~/.zsh_sessions",
    "~/.bash_sessions",

]

# ----------------------------------------------------------
# Cleaning process
# ----------------------------------------------------------

print("\n==============================")
print("MAC CACHE CLEANER STARTED")
print("==============================\n")

for path in locations:

    expanded = Path(path).expanduser()

    print("\nCleaning:", expanded)

    clean_folder(expanded)

# ----------------------------------------------------------
# Reset clipboard
# ----------------------------------------------------------

print("\nResetting clipboard...\n")
run_cmd("pbcopy < /dev/null")

# ----------------------------------------------------------
# Clear shell history (optional)
# ----------------------------------------------------------

print("Clearing terminal history...\n")

delete_item(Path("~/.zsh_history").expanduser())
delete_item(Path("~/.bash_history").expanduser())

# ----------------------------------------------------------
# Flush DNS cache
# ----------------------------------------------------------

print("\nFlushing DNS cache...\n")

run_cmd("sudo dscacheutil -flushcache")
run_cmd("sudo killall -HUP mDNSResponder")

# ----------------------------------------------------------
# Finished
# ----------------------------------------------------------

print("\n==============================")
print("CACHE CLEANING COMPLETE")
print("==============================\n")

# ----------------------------------------------------------
# Ask restart
# ----------------------------------------------------------

answer = input("Do you want to restart now? (y/n): ").strip().lower()

if answer == "y":

    print("\nRestarting system...\n")

    run_cmd("sudo shutdown -r now")

else:

    print("\nRestart skipped.")