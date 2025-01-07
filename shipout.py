#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess

def clear_dist_folder(directory):
    """Clears the contents of the /dist folder without deleting the folder itself."""
    dist_path = os.path.join(directory, 'dist')
    if not os.path.exists(dist_path):
        print(f"The folder {dist_path} does not exist.")
        return

    # Iterate through all files in the /dist folder and delete them
    for item in os.listdir(dist_path):
        item_path = os.path.join(dist_path, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        else:
            print(f"Skipping {item_path} because it is not a file.")

def main():
    # Check for directory argument
    if len(sys.argv) != 2:
        print("Usage: python shipout.py <directory>")
        sys.exit(1)

    # Get the directory from the command line argument
    directory = sys.argv[1]

    # Ensure the argument is a valid directory
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.")
        sys.exit(1)

    # Clear the /dist folder inside the directory
    clear_dist_folder(directory)

    # Change working directory to the target directory
    os.chdir(directory)

    # Run `python3 -m build`
    try:
        subprocess.run(["python3", "-m", "build"], check=True)
    except subprocess.CalledProcessError as e:
        print("Error occurred during build process:", e)
        sys.exit(1)

    # Run `python3 -m twine upload dist/*`
    try:
        subprocess.run(["python3", "-m", "twine", "upload", "dist/*"], check=True)
    except subprocess.CalledProcessError as e:
        print("Error occurred during upload process:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
