# import subprocess
# import sys

# def edit_file(file_path):
#     """
#     Opens a file in a text editor for editing and waits for the editor to close on a Mac.
    
#     Args:
#     file_path (str): The path to the file to be edited.
#     """
#     try:
#         # Specify the name of the application you want to use
#         app_name = "Visual Studio Code"  # Change to your preferred editor, e.g., "Sublime Text"
        
#         # Open the file using the specified application
#         subprocess.run(["open", "-a", app_name, file_path])
        
#         print(f"Finished opening {file_path} in {app_name}")
#     except Exception as e:
#         print(f"Error opening file: {e}")
#         sys.exit(1)

import subprocess
import sys

def edit_file(file_path):
    """
    Opens a file in a text editor for editing and waits for the editor to close on a Mac.
    
    Args:
    file_path (str): The path to the file to be edited.
    """
    try:
        # Specify the name of the application you want to use
        app_name = "TextEdit"  # Change to your preferred editor, e.g., "Sublime Text"
        
        # Open the file using the specified application
        subprocess.run(["open", "-a", app_name, file_path])
        
        print(f"Finished opening {file_path} in {app_name}")
    except Exception as e:
        print(f"Error opening file: {e}")
        sys.exit(1)

# Example usage
# edit_file("/path/to/your/file.txt")
