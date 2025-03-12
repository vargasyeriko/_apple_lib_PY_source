import subprocess
import os
import sys
from datetime import datetime

# Set your git repository path (change it to your repo's path)
repo_path = "/Users/yerik/_apple_lib/_g_GIT"

# Navigate to the repository
os.chdir(repo_path)

def git_command(command):
    """Helper function to run a Git command and capture the output."""
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Error running command: {command}\n{result.stderr}")
        sys.exit(1)
    return result.stdout

def check_status():
    """Check the current status of the git repo."""
    status = git_command(["git", "status"])
    print(status)

def add_changes():
    """Stage all changes."""
    print("Staging all changes...")
    git_command(["git", "add", "-A"])

def commit_changes():
    """Commit the changes with a timestamp message."""
    commit_message = f"Auto commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    print(f"Committing changes: {commit_message}")
    git_command(["git", "commit", "-m", commit_message])

def push_changes():
    """Push the changes to the remote repository."""
    print("Pushing changes to GitHub...")
    git_command(["git", "push"])

def git_push_automation():
    """Automate the process of staging, committing, and pushing."""
    check_status()
    add_changes()
    commit_changes()
    push_changes()

if __name__ == "__main__":
    git_push_automation()
    print("Git push automation completed successfully!")
