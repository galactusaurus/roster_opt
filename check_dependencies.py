#!/usr/bin/env python3
"""
Simple test script to check if all required packages are installed.
This can help identify dependency issues that might cause tests to fail.
"""

import sys
import importlib

def check_dependencies():
    """Check if all required packages are installed and can be imported."""
    required_packages = [
        # Main dependencies
        'pandas',
        'numpy',
        'pulp',
        'requests',
        
        # Testing dependencies
        'pytest',
        'unittest',
        'coverage'
    ]
    
    missing_packages = []
    problematic_packages = []
    
    print("Checking required packages...")
    print("-" * 50)
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is NOT installed")
            missing_packages.append(package)
        except Exception as e:
            print(f"! {package} has issues: {str(e)}")
            problematic_packages.append((package, str(e)))
    
    print("-" * 50)
    if not missing_packages and not problematic_packages:
        print("All dependencies are installed and working correctly!")
        return True
    
    if missing_packages:
        print("\nMissing packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall them using:")
        print(f"  python -m pip install {' '.join(missing_packages)} --user")
    
    if problematic_packages:
        print("\nPackages with issues:")
        for package, error in problematic_packages:
            print(f"  - {package}: {error}")
    
    return False

if __name__ == "__main__":
    success = check_dependencies()
    sys.exit(0 if success else 1)
