import requests
import os

# Load token from environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# GitHub credentials
GITHUB_USERNAME = "vargasyeriko"
REPO_NAME = "_apple_lib_PY_source"
REPO_DESCRIPTION = "Python source repository for Apple Library"
PRIVATE = False  # Change to True if you want it private

# GitHub API URL
url = "https://api.github.com/user/repos"
headers = {"Authorization": f"token {GITHUB_TOKEN}"}
data = {"name": REPO_NAME, "description": REPO_DESCRIPTION, "private": PRIVATE}

# Create the repo
response = requests.post(url, json=data, headers=headers)
if response.status_code == 201:
    print(f"✅ Successfully created GitHub repository: {REPO_NAME}")
    print(f"🔗 Repository URL: https://github.com/{GITHUB_USERNAME}/{REPO_NAME}.git")
else:
    print(f"❌ Failed to create repository: {response.json()}")
