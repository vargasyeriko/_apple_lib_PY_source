import shutil
import os
import time
from pathlib import Path

# ------######------ BACKUP SCRIPT ------######------

def compare_folders(src, dst):
    """
    Compare source and destination folders, returning new, modified, and deleted files.
    """
    new_files, modified_files, deleted_files = [], [], []

    # Define files to ignore
    ignored_extensions = {".c~", ".DS_Store", "Thumbs.db"}

    # Get all files in source and destination
    src_files = {}
    for root, _, files in os.walk(src):
        for file in files:
            file_path = Path(root) / file

            if any(file.endswith(ext) for ext in ignored_extensions):
                continue  # Ignore temp/system files

            try:
                src_files[str(file_path)] = os.stat(file_path).st_mtime
            except FileNotFoundError:
                continue  # Just skip missing files

    dst_files = {}
    for root, _, files in os.walk(dst):
        for file in files:
            file_path = Path(root) / file

            if any(file.endswith(ext) for ext in ignored_extensions):
                continue

            try:
                dst_files[str(file_path)] = os.stat(file_path).st_mtime
            except FileNotFoundError:
                continue

    # Check for new and modified files
    for file_path, src_time in src_files.items():
        rel_path = str(Path(file_path).relative_to(src))
        dst_path = str(Path(dst) / rel_path)

        if dst_path not in dst_files:
            new_files.append(rel_path)
        elif src_time > dst_files[dst_path]:  # Compare timestamps
            modified_files.append(rel_path)

    # Check for deleted files
    for file_path in dst_files:
        rel_path = str(Path(file_path).relative_to(dst))
        src_path = str(Path(src) / rel_path)

        if src_path not in src_files:
            deleted_files.append(rel_path)

    return new_files, modified_files, deleted_files


def _backup_folders_sync_1703(source_folder1, source_folder2, destination):
    """
    Syncs source folders with the destination, automatically handling updates.

    Args:
        source_folder1 (str): Path to the first folder to copy.
        source_folder2 (str): Path to the second folder to copy.
        destination (str): Path to the destination where folders will be synced.
    """

    # Check if source folders exist
    if not os.path.exists(source_folder1) or not os.path.exists(source_folder2):
        print("❌ Error: One or both source folders do not exist.")
        return

    # Define target paths
    dest_folder1 = os.path.join(destination, os.path.basename(source_folder1))
    dest_folder2 = os.path.join(destination, os.path.basename(source_folder2))

    print("\n🔍 Checking for updates...\n")

    changes = []
    for src, dst in [(source_folder1, dest_folder1), (source_folder2, dest_folder2)]:
        if not os.path.exists(dst):
            print(f"📂 {os.path.basename(src)} → Destination does not exist (will be fully copied).")
            changes.append((src, dst, "FULL_COPY"))
        else:
            new_files, modified_files, deleted_files = compare_folders(src, dst)
            total_changes = len(new_files) + len(modified_files) + len(deleted_files)

            if total_changes > 0:
                print(f"🔄 {os.path.basename(src)} has {total_changes} changes:")
                print(f" ➕ {len(new_files)} new files")
                print(f" ✏ {len(modified_files)} modified files")
                print(f" ❌ {len(deleted_files)} deleted files")

                # Auto-remove deleted files
                for rel_path in deleted_files:
                    delete_path = os.path.join(dst, rel_path)
                    if os.path.exists(delete_path):
                        os.remove(delete_path)
                print("🗑 Deleted files removed.")

                changes.append((src, dst, "PARTIAL_COPY"))

    if not changes:
        print("✅ No changes detected. Everything is up to date.")
        return

    # Start timing
    total_start_time = time.time()

    # Sync Folders
    for src, dst, sync_type in changes:
        start_time = time.time()

        if sync_type == "FULL_COPY":
            if os.path.exists(dst):
                print(f"🗑 Removing existing folder: {dst}")
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            # Copy new & modified files
            for root, _, files in os.walk(src):
                rel_path = Path(root).relative_to(src)
                dest_path = Path(dst) / rel_path
                dest_path.mkdir(parents=True, exist_ok=True)

                for file in files:
                    src_file = Path(root) / file
                    dest_file = dest_path / file

                    if not src_file.exists():  # Skip if source file is missing
                        continue

                    if not dest_file.exists() or os.stat(src_file).st_mtime > os.stat(dest_file).st_mtime:
                        shutil.copy2(src_file, dest_file)  # Preserve metadata

        elapsed_time = time.time() - start_time
        print(f"✔ TQM: {os.path.basename(src)} synced in {elapsed_time:.2f} seconds.")

    total_elapsed_time = time.time() - total_start_time
    print(f"\n🚀 TQM: Total sync time: {total_elapsed_time:.2f} seconds.")


# !#!#!#!#! RUNNING STATEMENTS #!#!#!#!#!
# Example Usage
_backup_folders_sync_1703(
    "/Users/yerik/_apple_lib/_b_envs",
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


