# Helper script to copy the DraftKings salary file from Downloads to the project directory
# This script is optional and for convenience only

import os
import shutil
import time
from pathlib import Path
from datetime import datetime

def main():
    """Copy the latest DraftKings salary file from Downloads to the project directory."""
    # Find user's Downloads folder
    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    
    # Look for all DraftKings salary files and get the most recent one
    dk_files = []
    for file in os.listdir(downloads_dir):
        if file.startswith("DKSalaries") and file.endswith(".csv"):
            file_path = os.path.join(downloads_dir, file)
            # Get file modification time
            mod_time = os.path.getmtime(file_path)
            # Create a readable time string
            time_str = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
            dk_files.append((file_path, mod_time, time_str))
    
    # Sort files by modification time (newest first)
    dk_files.sort(key=lambda x: x[1], reverse=True)
    
    if not dk_files:
        return None
        
    # By default, use the most recent file
    file_index = 0
    
    # If multiple files found, give the user the option to choose
    if len(dk_files) > 1:
        print(f"Found {len(dk_files)} DraftKings salary files:")
        
        # Ask if the user wants to select a specific file
        print("\nOptions:")
        print("1. Use the most recent file automatically")
        print("2. Select from the list of available files")
        
        choice = input("\nEnter your choice (1-2) [default=1]: ").strip() or "1"
        
        if choice == "2":
            # Display files for selection
            print("\nAvailable files (newest first):")
            for i, (file_path, _, time_str) in enumerate(dk_files[:10], 1):  # Show at most 10 files
                print(f"{i}. {os.path.basename(file_path)} - Modified: {time_str}")
                
            if len(dk_files) > 10:
                print(f"... and {len(dk_files) - 10} more files")
                
            # Get user selection
            while True:
                try:
                    selection = input("\nEnter the number of the file to use [default=1]: ").strip() or "1"
                    file_index = int(selection) - 1
                    if 0 <= file_index < len(dk_files):
                        break
                    else:
                        print(f"Please enter a number between 1 and {min(len(dk_files), 10)}")
                except ValueError:
                    print("Please enter a valid number")
        else:
            print(f"\nUsing the most recent file: {os.path.basename(dk_files[0][0])}")
    
    # Get the selected file
    dk_file = dk_files[file_index][0]
    
    if not dk_file:
        print("Could not find any DraftKings salary files in your Downloads folder.")
        print("Please download the file or place it manually in this directory.")
        return
    
    # Get the file's modification date and time
    mod_time = datetime.fromtimestamp(os.path.getmtime(dk_file))
    mod_time_str = mod_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Copy the file to the current directory
    dest_file = os.path.join(os.getcwd(), "DKSalaries.csv")
    try:
        shutil.copy2(dk_file, dest_file)
        print(f"Successfully copied the latest DraftKings file:")
        print(f"  Source: {dk_file}")
        print(f"  Last modified: {mod_time_str}")
        print(f"  Destination: {dest_file}")
    except Exception as e:
        print(f"Error copying file: {e}")

if __name__ == "__main__":
    main()
