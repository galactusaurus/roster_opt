#!/usr/bin/env python3
"""
Setup script to install requirements for running tests.
"""

import subprocess
import sys
import os


def install_requirements():
    """Install required packages for testing."""
    print("Installing required packages for testing...")
    
    # Basic requirements (should already be installed)
    required_packages = [
        'pandas',
        'pulp',
        'numpy',
        'requests'
    ]
    
    # Additional testing packages
    test_packages = [
        'pytest',
        'coverage'
    ]
    
    # Install one package at a time with --user flag to avoid permission issues
    all_success = True
    
    # First upgrade pip to latest version
    try:
        print("Upgrading pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--user"])
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not upgrade pip: {e}")
        # Continue anyway, not critical
    
    # Install each package separately with --user flag
    for package in required_packages + test_packages:
        print(f"Installing {package}...")
        try:
            # Use --user flag to install to user directory, avoiding permission issues
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--user"])
        except subprocess.CalledProcessError as e:
            print(f"\nError installing {package}: {e}")
            all_success = False
            # Continue with other packages
    
    if all_success:
        print("\nAll requirements installed successfully!")
    else:
        print("\nSome packages failed to install. You may need to manually install them.")
        print("Try running: python -m pip install pandas pulp numpy requests pytest coverage --user")
    
    return all_success


def setup_test_environment():
    """Create necessary test directories if they don't exist."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # MLB Optimizer test directory
    mlb_test_dir = os.path.join(base_dir, 'MLB_Optimizer', 'tests')
    if not os.path.exists(mlb_test_dir):
        os.makedirs(mlb_test_dir)
        print(f"Created MLB test directory: {mlb_test_dir}")
    
    # F1 Optimizer test directory
    f1_test_dir = os.path.join(base_dir, 'F1_Optimizer', 'tests')
    if not os.path.exists(f1_test_dir):
        os.makedirs(f1_test_dir)
        print(f"Created F1 test directory: {f1_test_dir}")
    
    return True


if __name__ == "__main__":
    print("Setting up test environment for roster optimizers...")
    
    if install_requirements() and setup_test_environment():
        print("\nSetup complete! You can now run tests using:")
        print("  python run_tests.py")
        print("  or")
        print("  run_tests.bat")
    else:
        print("\nSetup failed. Please check the error messages above.")
        sys.exit(1)
