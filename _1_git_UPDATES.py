import shutil
import os
import time
from pathlib import Path

# ------######------ OPTIMIZED BACKUP SCRIPT ------######------

def compare_folders(src, dst):
    """
    Compare source and destination folders, returning new, modified, and deleted files.
    Faster implementation using os.scandir().
    """
    new_files, modified_files, deleted_files = [], [], []

    ignored_extensions = {".c~", ".DS_Store", "Thumbs.db"}

    src_files = {}
    dst_files = {}

    # Use os.scandir() for faster file iteration
    def scan_folder(base_path, file_dict):
        for root, _, files in os.walk(base_path):
            for file in files:
                file_path = Path(root) / file
                if any(file.endswith(ext) for ext in ignored_extensions):
                    continue
                try:
                    file_dict[str(file_path)] = os.stat(file_path).st_mtime
                except FileNotFoundError:
                    continue

    scan_folder(src, src_files)
    scan_folder(dst, dst_files)

    for file_path, src_time in src_files.items():
        rel_path = str(Path(file_path).relative_to(src))
        dst_path = str(Path(dst) / rel_path)

        if dst_path not in dst_files:
            new_files.append(rel_path)
        elif src_time > dst_files[dst_path]:  # Compare timestamps
            modified_files.append(rel_path)

    for file_path in dst_files:
        rel_path = str(Path(file_path).relative_to(dst))
        src_path = str(Path(src) / rel_path)

        if src_path not in src_files:
            deleted_files.append(rel_path)

    return new_files, modified_files, deleted_files


def _backup_folder_sync_1703(source_folder, destination):
    """
    Optimized sync function for backing up a single folder (_a_progs).
    """
    if not os.path.exists(source_folder):
        print("❌ Error: Source folder does not exist.")
        return

    dest_folder = os.path.join(destination, os.path.basename(source_folder))

    print("\n🔍 Checking for updates...\n")

    # Compare and find changes
    if not os.path.exists(dest_folder):
        print(f"📂 {os.path.basename(source_folder)} → Destination does not exist (full copy).")
        sync_type = "FULL_COPY"
    else:
        new_files, modified_files, deleted_files = compare_folders(source_folder, dest_folder)
        total_changes = len(new_files) + len(modified_files) + len(deleted_files)

        if total_changes == 0:
            print("✅ No changes detected. Everything is up to date.")
            return

        print(f"🔄 {os.path.basename(source_folder)} has {total_changes} changes:")
        print(f" ➕ {len(new_files)} new files")
        print(f" ✏ {len(modified_files)} modified files")
        print(f" ❌ {len(deleted_files)} deleted files")

        # Auto-remove deleted files
        for rel_path in deleted_files:
            delete_path = os.path.join(dest_folder, rel_path)
            if os.path.exists(delete_path):
                os.remove(delete_path)
        print("🗑 Deleted files removed.")

        sync_type = "PARTIAL_COPY"

    # Start timing
    start_time = time.time()

    if sync_type == "FULL_COPY":
        if os.path.exists(dest_folder):
            print(f"🗑 Removing existing folder: {dest_folder}")
            shutil.rmtree(dest_folder)
        shutil.copytree(source_folder, dest_folder)
    else:
        # Copy new & modified files
        for root, _, files in os.walk(source_folder):
            rel_path = Path(root).relative_to(source_folder)
            dest_path = Path(dest_folder) / rel_path
            dest_path.mkdir(parents=True, exist_ok=True)

            for file in files:
                src_file = Path(root) / file
                dest_file = dest_path / file

                if not src_file.exists():  # Skip if source file is missing
                    continue

                if not dest_file.exists() or os.stat(src_file).st_mtime > os.stat(dest_file).st_mtime:
                    shutil.copy2(src_file, dest_file)  # Preserve metadata

    elapsed_time = time.time() - start_time
    print(f"\n🚀 TQM: {os.path.basename(source_folder)} synced in {elapsed_time:.2f} seconds.")


# !#!#!#!#! RUNNING STATEMENTS #!#!#!#!#!
# Example Usage - Now syncing only _a_progs
_backup_folder_sync_1703(
    "/Users/yerik/_apple_lib/_a_progs",
    "/Users/yerik/_apple_lib/_g_GIT"
)


############################### new_add GIT

import subprocess
import os
import sys
from datetime import datetime

 
# Set your repository name and GitHub username
GITHUB_USERNAME = "vargasyeriko"
REPO_NAME = "_apple_lib_PY_source"
REPO_DESCRIPTION = "Python source repository for Apple Library"
LOCAL_PATH = "/Users/yerik/_apple_lib/_g_GIT"  # Path to your local directory

# Your GitHub token (set this securely using environment variables or a .env file)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# GitHub API URL
GITHUB_API_URL = "https://api.github.com/user/repos"

def run_git_command(command):
    """Helper function to run a Git command and capture output"""
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Error running command: {command}\n{result.stderr}")
        sys.exit(1)
    return result.stdout

def check_status():
    """Check the current status of the git repo"""
    status = run_git_command(["git", "status"])
    return status

def initialize_local_repo():
    """Initialize a local Git repository"""
    if not os.path.exists(LOCAL_PATH):
        os.makedirs(LOCAL_PATH)

    os.chdir(LOCAL_PATH)
    
    print("Initializing local repository...")
    run_git_command(["git", "init"])

    # Create a basic .gitignore and README
    with open(".gitignore", "w") as f:
        f.write(".env\n__pycache__/\n*.pyc\n.DS_Store\n")
    
    with open("README.md", "w") as f:
        f.write(f"# {REPO_NAME}\n{REPO_DESCRIPTION}\n")

    print("Local repository initialized.")

def create_github_repo():
    """Create a GitHub repository using GitHub API"""
    if not GITHUB_TOKEN:
        print("Error: GitHub token is not set. Please set your GitHub token.")
        sys.exit(1)
    
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    data = {"name": REPO_NAME, "description": REPO_DESCRIPTION, "private": False}

    response = subprocess.run(
        ["curl", "-X", "POST", GITHUB_API_URL, "-H", f"Authorization: token {GITHUB_TOKEN}", "-d", str(data)],
        capture_output=True, text=True
    )

    if response.returncode != 0:
        print(f"Failed to create GitHub repository: {response.stderr}")
        sys.exit(1)

    print("GitHub repository created successfully!")

def add_remote_and_push():
    """Set remote origin and push the changes to GitHub"""
    run_git_command(["git", "remote", "add", "origin", f"https://github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"])
    run_git_command(["git", "branch", "-M", "main"])
    
    print("Pushing to GitHub...")
    run_git_command(["git", "push", "-u", "origin", "main"])

def stage_and_commit_push():
    """Stage, commit, and push changes to GitHub"""
    print("Staging all changes...")
    run_git_command(["git", "add", "-A"])

    # Check if there are changes to commit
    status = check_status()
    if "nothing to commit" in status:
        print("No changes detected, skipping commit and push.")
    else:
        commit_message = f"Auto commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        print(f"Committing changes: {commit_message}")
        run_git_command(["git", "commit", "-m", commit_message])
        print("Pushing changes to GitHub...")
        run_git_command(["git", "push"])

def git_auto_repo():
    """Automate the entire Git workflow: Init, commit, push."""
    # Check if repo exists and do not initialize again
    if not os.path.isdir(LOCAL_PATH + "/.git"):
        initialize_local_repo()
        create_github_repo()
    else:
        print("Git repository already initialized.")

    # Run the push automation
    stage_and_commit_push()

if __name__ == "__main__":
    git_auto_repo()
    print("Git repo is up to date and successfully pushed!")


