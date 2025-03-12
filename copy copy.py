import subprocess
import os

# Define paths
GIT_DIR = "/Users/yerik/_apple_source/__git"
TRACKED_DIR = "/Users/yerik/_apple_lib"
GIT_REPO_URL = "your-git-repo-url"  # Change this to your Git repository

# Function to check if Git is installed
def check_git():
    try:
        subprocess.run(["git", "--version"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

# Function to initialize Git if not already initialized
def setup_git():
    os.chdir(GIT_DIR)
    if not os.path.exists(f"{GIT_DIR}/.git"):
        print("🛠  Initializing Git repository in", GIT_DIR)
        subprocess.run(["git", "init"])
        subprocess.run(["git", "remote", "add", "origin", GIT_REPO_URL])
        subprocess.run(["git", "branch", "-M", "main"])
        print("✅ Git repository initialized.")

# Function to schedule automatic tracking
def setup_cron():
    print("⏳ Setting up automatic tracking...")
    cron_command = f"*/30 * * * * /bin/bash {GIT_DIR}/setup_env.sh"

    # Add the cron job
    subprocess.run(f"(crontab -l 2>/dev/null; echo \"{cron_command}\") | crontab -", shell=True)
    print("✅ Cron job scheduled to run every 30 minutes.")

if __name__ == "__main__":
    print("\n🌟=============================================🌟")
    print("       🚀 ONE-TIME SETUP & AUTOMATION 🚀        ")
    print("🌟=============================================🌟\n")

    # Check for Git
    if check_git():
        print("✅ Git is installed.")
    else:
        print("❌ Git is not installed. Please install it first.")
        exit(1)

    # Ensure the Git directory exists
    if not os.path.exists(GIT_DIR):
        os.makedirs(GIT_DIR)
        print(f"📂 Created Git directory: {GIT_DIR}")

    # Setup Git
    setup_git()

    # Schedule the tracking automation
    setup_cron()

    print("\n🎉 Setup complete! 🚀 Your system will now automatically track changes in `/Users/yerik/_apple_lib/`.\n")
