import shutil
import os
import time

# ------######------ BACKUP SCRIPT ------######------
def _backup_folders_replace_1103(source_folder1, source_folder2, destination):
    """
    Replaces existing destination folders with source folders.
    Deletes existing destination folders before copying the new ones.

    Args:
        source_folder1 (str): Path to the first folder to copy.
        source_folder2 (str): Path to the second folder to copy.
        destination (str): Path to the destination where folders will be replaced.
    """
    
    # Ask user for confirmation
    user_input = input("Do you want to update the Git folders? (y to proceed): ").strip().lower()
    if user_input != "y":
        print("Operation canceled. No changes made.")
        return

    if not os.path.exists(source_folder1) or not os.path.exists(source_folder2):
        print("Error: One or both source folders do not exist.")
        return

    # Define target paths
    dest_folder1 = os.path.join(destination, os.path.basename(source_folder1))
    dest_folder2 = os.path.join(destination, os.path.basename(source_folder2))

    # Remove existing destination folders
    for dest_folder in [dest_folder1, dest_folder2]:
        if os.path.exists(dest_folder):
            print(f"Removing existing folder: {dest_folder}")
            shutil.rmtree(dest_folder)

    # Start timing
    total_start_time = time.time()

    # Copy source folders to destination
    start_time = time.time()
    shutil.copytree(source_folder1, dest_folder1)
    elapsed_time1 = time.time() - start_time
    print(f"✔ TQM: {source_folder1} copied in {elapsed_time1:.2f} seconds.")

    start_time = time.time()
    shutil.copytree(source_folder2, dest_folder2)
    elapsed_time2 = time.time() - start_time
    print(f"✔ TQM: {source_folder2} copied in {elapsed_time2:.2f} seconds.")

    # Total time
    total_elapsed_time = time.time() - total_start_time
    print(f"✔ TQM: Total backup time: {total_elapsed_time:.2f} seconds 🚀")

    print(f"Backup complete: {source_folder1} and {source_folder2} → {destination}")

# !#!#!#!#! RUNNING STATEMENTS #!#!#!#!#!
# Example Usage
_backup_folders_replace_1103("/Users/yerik/_apple_lib/_b_envs", "/Users/yerik/_apple_lib/_a_progs", "/Users/yerik/_apple_lib/_g_GIT")
