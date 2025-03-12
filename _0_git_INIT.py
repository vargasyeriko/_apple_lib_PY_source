import os
import subprocess
import requests

# GitHub credentials and repo details
GITHUB_USERNAME = "vargasyeriko"
GITHUB_TOKEN = "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"
REPO_NAME = "_py_tree_"
REPO_DESCRIPTION = "Showcase use application PYTHON"
LOCAL_PATH = "/Users/yerik/_apple_lib/_g_GIT"

# Create a local repository
def initialize_local_repo():
    os.makedirs(LOCAL_PATH, exist_ok=True)
    os.chdir(LOCAL_PATH)
    
    subprocess.run(["git", "init"], check=True)
    subprocess.run(["touch", ".gitignore"], check=True)
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)

# Create a GitHub repo using GitHub API
def create_github_repo():
    url = "https://api.github.com/user/repos"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    data = {"name": REPO_NAME, "description": REPO_DESCRIPTION, "private": False}

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        print("GitHub repository created successfully!")
        return f"https://github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"
    else:
        print("Failed to create GitHub repository:", response.json())
        return None

# Link local repo to GitHub and push
def link_and_push(remote_url):
    subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)
    subprocess.run(["git", "branch", "-M", "main"], check=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], check=True)

if __name__ == "__main__":
    initialize_local_repo()
    remote_url = create_github_repo()
    if remote_url:
        link_and_push(remote_url)
