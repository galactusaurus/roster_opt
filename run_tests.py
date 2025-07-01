#!/usr/bin/env python3
"""
Main test runner script for the roster optimization project.

This script discovers and runs all tests for both MLB and F1 optimizers.
"""

import os
import sys
import unittest
import argparse
import datetime


def check_required_packages():
    """Check if required packages are installed."""
    required_packages = ['pandas', 'pulp', 'numpy', 'requests', 'pytest']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("ERROR: The following required packages are missing:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nPlease install them using:")
        print(f"  python -m pip install {' '.join(missing_packages)} --user")
        print("\nOr run setup_tests.bat to install all required packages.")
        return False
    
    return True


def run_tests():
    """Run all tests or tests for a specific optimizer."""
    # First check if required packages are available
    if not check_required_packages():
        return 1
    
    parser = argparse.ArgumentParser(description='Run tests for the roster optimizers')
    parser.add_argument('--optimizer', choices=['mlb', 'f1', 'all'], default='all',
                        help='Which optimizer tests to run (mlb, f1, or all)')
    args = parser.parse_args()
    
    # Get the base directory of the project
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Print some environment information for the log
    print(f"Python version: {sys.version}")
    print(f"Testing directory: {base_dir}")
    print(f"Date and time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 70)
    
    # Build the test suite based on command line arguments
    test_suite = unittest.TestSuite()
    test_count = 0
    
    if args.optimizer in ['mlb', 'all']:
        print("\nDiscovering MLB optimizer tests...")
        mlb_test_dir = os.path.join(base_dir, 'MLB_Optimizer', 'tests')
        if os.path.exists(mlb_test_dir):
            try:
                mlb_tests = unittest.defaultTestLoader.discover(mlb_test_dir, pattern='test_*.py')
                test_suite.addTest(mlb_tests)
                mlb_count = sum(1 for _ in mlb_tests)
                test_count += mlb_count
                print(f"Found {mlb_count} MLB test cases in {mlb_test_dir}")
                # List the test files found
                test_files = [os.path.basename(f) for f in os.listdir(mlb_test_dir) if f.startswith('test_') and f.endswith('.py')]
                print(f"MLB test files: {', '.join(test_files)}")
            except Exception as e:
                print(f"Error discovering MLB tests: {e}")
                print("Make sure MLB_Optimizer has all the required files.")
        else:
            print(f"Warning: MLB test directory not found at {mlb_test_dir}")
            print("Creating the directory now...")
            try:
                os.makedirs(mlb_test_dir, exist_ok=True)
            except Exception as e:
                print(f"Error creating directory: {e}")
    
    if args.optimizer in ['f1', 'all']:
        print("\nDiscovering F1 optimizer tests...")
        f1_test_dir = os.path.join(base_dir, 'F1_Optimizer', 'tests')
        if os.path.exists(f1_test_dir):
            try:
                f1_tests = unittest.defaultTestLoader.discover(f1_test_dir, pattern='test_*.py')
                test_suite.addTest(f1_tests)
                f1_count = sum(1 for _ in f1_tests)
                test_count += f1_count
                print(f"Found {f1_count} F1 test cases in {f1_test_dir}")
                # List the test files found
                test_files = [os.path.basename(f) for f in os.listdir(f1_test_dir) if f.startswith('test_') and f.endswith('.py')]
                print(f"F1 test files: {', '.join(test_files)}")
            except Exception as e:
                print(f"Error discovering F1 tests: {e}")
                print("Make sure F1_Optimizer has all the required files.")
        else:
            print(f"Warning: F1 test directory not found at {f1_test_dir}")
            print("Creating the directory now...")
            try:
                os.makedirs(f1_test_dir, exist_ok=True)
            except Exception as e:
                print(f"Error creating directory: {e}")
    
    # Run the tests
    print("\nRunning tests...")
    print(f"Total test cases to run: {test_count}")
    print("-" * 70)
    
    start_time = datetime.datetime.now()
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    end_time = datetime.datetime.now()
    duration = end_time - start_time
    
    # Print test summary
    print("\nTest Summary:")
    print("-" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print(f"Test duration: {duration.total_seconds():.2f} seconds")
    
    if result.wasSuccessful():
        print("\nAll tests PASSED!")
    else:
        print("\nSome tests FAILED.")
        
        if result.failures:
            print("\nFailure details:")
            for i, (test, traceback) in enumerate(result.failures, 1):
                print(f"\n{i}. {test}")
                print("-" * 40)
                print(traceback)
                print("-" * 40)
        
        if result.errors:
            print("\nError details:")
            for i, (test, traceback) in enumerate(result.errors, 1):
                print(f"\n{i}. {test}")
                print("-" * 40)
                print(traceback)
                print("-" * 40)
    
    # Return appropriate exit code based on test results
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    try:
        sys.exit(run_tests())
    except Exception as e:
        print(f"\nError running tests: {e}")
        sys.exit(1)
