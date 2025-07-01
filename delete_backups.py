"""
Script to delete all backup (.bak) files in the project directory.
"""
import os
import glob

def delete_backup_files():
    """Delete all backup files (*.bak) in the project directory and subdirectories."""
    count = 0
    
    # Find and delete all .bak files in the current directory and subdirectories
    for backup_file in glob.glob('**/*.bak*', recursive=True):
        try:
            os.remove(backup_file)
            print(f"Deleted: {backup_file}")
            count += 1
        except Exception as e:
            print(f"Error deleting {backup_file}: {e}")
    
    return count

if __name__ == '__main__':
    print("Deleting backup files...")
    count = delete_backup_files()
    print(f"\nOperation complete: {count} backup files deleted.")
