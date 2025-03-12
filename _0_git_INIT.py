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
    print(status)

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
