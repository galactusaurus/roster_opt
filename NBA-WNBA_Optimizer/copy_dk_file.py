#!/usr/bin/env python3
"""
Utility to find and copy the latest DraftKings salaries file to the NBA-WNBA_Optimizer directory.
This makes it easier to find and use the latest salaries file for NBA/WNBA contests.
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
        print("No DraftKings salaries file found in Downloads folder.")
        print("Please download the DraftKings NBA/WNBA salaries CSV file first.")
        return
    
    # Get file info
    file_time = os.path.getmtime(latest_file)
    file_date = datetime.fromtimestamp(file_time).strftime("%Y-%m-%d %H:%M:%S")
    file_name = os.path.basename(latest_file)
    
    print(f"Found: {file_name}")
    print(f"Modified: {file_date}")
    
    # Copy to current directory as DKSalaries.csv
    destination = "DKSalaries.csv"
    
    try:
        shutil.copy2(latest_file, destination)
        print(f"Successfully copied to {destination}")
        print("Ready to run NBA/WNBA optimizer!")
    except Exception as e:
        print(f"Error copying file: {e}")

if __name__ == "__main__":
    main()
