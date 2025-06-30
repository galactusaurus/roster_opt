#!/usr/bin/env python3
"""
MLB Injury File Manager

This script helps with finding, analyzing, and managing MLB injury files.
It provides utilities to:
- Search for and list available injury files
- Preview the contents of injury files
- Download the latest MLB injury report if needed
"""

import os
import sys
import pandas as pd
import glob
from datetime import datetime
import shutil
import requests
from urllib.parse import urlparse

# Import the find_injured_list function from the advanced optimizer
try:
    from advanced_optimizer import find_injured_list
except ImportError:
    print("Could not import find_injured_list. Make sure advanced_optimizer.py is in the same directory.")
    sys.exit(1)


def list_all_injury_files():
    """Find and list all potential injury files."""
    # Look for common injury file patterns
    injury_patterns = ["mlb-injury*.csv", "*injury*.csv", "*injured*.csv", "*-IL-*.csv"]
    
    # Define search directories in priority order
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    user_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    
    search_dirs = [
        current_dir,                       # Current directory (MLB_Optimizer)
        parent_dir,                        # Parent directory (roster_opt)
        user_downloads,                    # User's Downloads folder
        os.path.join(parent_dir, "data"),  # Possible data directory
    ]
    
    all_matches = []
    
    # Find all matching files across directories
    for directory in search_dirs:
        if os.path.exists(directory):
            for pattern in injury_patterns:
                full_pattern = os.path.join(directory, pattern)
                matches = glob.glob(full_pattern)
                if matches:
                    for match in matches:
                        # Get file size and modified time
                        size = os.path.getsize(match)
                        mtime = os.path.getmtime(match)
                        mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                        all_matches.append((match, size, mtime, mtime_str))
    
    # Sort by modification time (newest first)
    all_matches.sort(key=lambda x: x[2], reverse=True)
    return all_matches


def preview_injury_file(file_path):
    """Preview the contents of an injury file."""
    try:
        df = pd.read_csv(file_path)
        
        print(f"\nPreview of: {file_path}")
        print(f"File size: {os.path.getsize(file_path)} bytes")
        print(f"Last modified: {datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Number of rows: {len(df)}")
        print(f"Columns: {', '.join(df.columns)}")
        
        # Try to identify the player name column
        name_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['name', 'player'])]
        if name_columns:
            name_col = name_columns[0]
            print(f"\nPreview of '{name_col}' column (first 10 entries):")
            for idx, name in enumerate(df[name_col].head(10).values):
                print(f"  {idx+1}. {name}")
        else:
            print("\nCouldn't identify player name column.")
            print("First 5 rows:")
            print(df.head())
    except Exception as e:
        print(f"Error reading the file: {str(e)}")


def download_latest_injury_report():
    """Attempt to download the latest MLB injury report."""
    # This is a placeholder function. In a real implementation, you would:
    # 1. Identify a reliable source for MLB injury data
    # 2. Use requests to download the data
    # 3. Save it to a file with appropriate naming
    
    print("This feature is not yet implemented.")
    print("To implement it, you would need to:")
    print("1. Identify a reliable API or website for MLB injury data")
    print("2. Implement a scraper or API client to fetch the data")
    print("3. Save the data to a CSV file in a standard format")
    print("\nFor now, please manually download injury reports and place them in the workspace.")


def copy_file_to_workspace(file_path):
    """Copy a file to the current workspace."""
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return False
    
    try:
        filename = os.path.basename(file_path)
        dest_path = os.path.join(os.getcwd(), filename)
        shutil.copy2(file_path, dest_path)
        print(f"Successfully copied {filename} to {os.getcwd()}")
        return True
    except Exception as e:
        print(f"Error copying file: {str(e)}")
        return False


def main():
    """Main function for the injury file manager."""
    print("\nMLB Injury File Manager")
    print("======================")
    
    while True:
        print("\nOptions:")
        print("1. Find most recent injury file")
        print("2. List all injury files")
        print("3. Preview an injury file")
        print("4. Copy an injury file to workspace")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == '1':
            print("\nSearching for the most recent injury file...")
            injury_file = find_injured_list()
            if injury_file:
                print(f"\nFound most recent injury file: {injury_file}")
                print(f"Last modified: {datetime.fromtimestamp(os.path.getmtime(injury_file)).strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print("\nNo injury files found.")
        
        elif choice == '2':
            print("\nSearching for all injury files...")
            files = list_all_injury_files()
            if files:
                print(f"\nFound {len(files)} potential injury files:")
                for i, (path, size, mtime, mtime_str) in enumerate(files, 1):
                    print(f"{i}. {path}")
                    print(f"   Size: {size} bytes, Last modified: {mtime_str}")
                    print()
            else:
                print("\nNo injury files found.")
        
        elif choice == '3':
            files = list_all_injury_files()
            if not files:
                print("\nNo injury files found.")
                continue
                
            print("\nAvailable injury files:")
            for i, (path, size, mtime, mtime_str) in enumerate(files, 1):
                print(f"{i}. {os.path.basename(path)} ({mtime_str})")
            
            try:
                idx = int(input("\nEnter file number to preview (0 to cancel): "))
                if idx == 0:
                    continue
                if 1 <= idx <= len(files):
                    preview_injury_file(files[idx-1][0])
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Please enter a valid number.")
        
        elif choice == '4':
            files = list_all_injury_files()
            if not files:
                print("\nNo injury files found to copy.")
                continue
                
            print("\nAvailable injury files to copy to workspace:")
            for i, (path, size, mtime, mtime_str) in enumerate(files, 1):
                print(f"{i}. {os.path.basename(path)} ({mtime_str})")
            
            try:
                idx = int(input("\nEnter file number to copy (0 to cancel): "))
                if idx == 0:
                    continue
                if 1 <= idx <= len(files):
                    copy_file_to_workspace(files[idx-1][0])
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Please enter a valid number.")
        
        elif choice == '5':
            print("\nExiting MLB Injury File Manager.")
            break
        
        else:
            print("\nInvalid choice. Please try again.")


if __name__ == "__main__":
    main()
