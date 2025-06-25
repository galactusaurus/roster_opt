#!/usr/bin/env python3
"""
Utility to find and copy the latest DraftKings salaries file to the F1_Optimizer directory.
This makes it easier to find and use the latest salaries file.
"""

import os
import glob
import shutil
from datetime import datetime

def find_latest_dk_file():
    """Find the latest DraftKings salaries file in the Downloads folder."""
    # Get the user's Downloads directory
    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    
    # Look for DK Salaries files
    pattern = os.path.join(downloads_dir, "DKSalaries*.csv")
    files = glob.glob(pattern)
    
    if not files:
        return None
        
    # Sort by modification time, newest first
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]

def main():
    # Find the latest DK salaries file
    latest_file = find_latest_dk_file()
    
    if not latest_file:
        print("No DraftKings salaries file found in your Downloads folder.")
        print("Please download the file from DraftKings first.")
        input("Press Enter to exit...")
        return
    
    # Get file name and current directory
    file_name = os.path.basename(latest_file)
    current_dir = os.getcwd()
    destination = os.path.join(current_dir, "DKSalaries.csv")
    
    # Copy the file
    try:
        shutil.copy2(latest_file, destination)
        print(f"Successfully copied {file_name} to {destination}")
        print(f"Original file: {latest_file}")
        print(f"Last modified: {datetime.fromtimestamp(os.path.getmtime(latest_file))}")
    except Exception as e:
        print(f"Error copying file: {e}")
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
