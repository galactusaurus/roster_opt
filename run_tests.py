#!/usr/bin/env python3
"""
Main test runner script for the roster optimization project.

This script discovers and runs all tests for MLB, F1, and NBA/WNBA optimizers.
"""

import os
import sys
import unittest
import argparse
import datetime
import subprocess


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
    parser.add_argument('--optimizer', choices=['mlb', 'f1', 'nba-wnba', 'all'], default='all',
                        help='Which optimizer tests to run (mlb, f1, nba-wnba, or all)')
    args = parser.parse_args()
    
    # Get the base directory of the project
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Print some environment information for the log
    print(f"Python version: {sys.version}")
    print(f"Testing directory: {base_dir}")
    print(f"Date and time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 70)
    
    # If running all tests, run each optimizer separately using subprocess to avoid module conflicts
    if args.optimizer == 'all':
        print("Running all optimizer tests separately to avoid module conflicts...")
        
        total_tests_run = 0
        total_failures = 0
        total_errors = 0
        total_skipped = 0
        overall_success = True
        
        start_time = datetime.datetime.now()
        
        # Run each optimizer's tests in a separate process
        for optimizer in ['mlb', 'f1', 'nba-wnba']:
            print(f"\n{'='*70}")
            print(f"Running {optimizer.upper()} tests...")
            print('='*70)
            
            # Run the test in a separate Python process
            cmd = [sys.executable, __file__, '--optimizer', optimizer]
            try:
                result = subprocess.run(cmd, cwd=base_dir, capture_output=True, text=True, check=False)
                print(result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)
                
                if result.returncode != 0:
                    overall_success = False
                    print(f"{optimizer.upper()} tests FAILED with return code {result.returncode}")
                else:
                    print(f"{optimizer.upper()} tests completed successfully")
                    
            except Exception as e:
                print(f"Error running {optimizer} tests: {e}")
                overall_success = False
        
        end_time = datetime.datetime.now()
        duration = end_time - start_time
        
        # Print overall summary
        print(f"\n{'='*70}")
        print("OVERALL TEST SUMMARY:")
        print('='*70)
        print(f"Total duration: {duration.total_seconds():.2f} seconds")
        
        if overall_success:
            print("\nAll tests PASSED!")
            return 0
        else:
            print("\nSome tests FAILED.")
            return 1
    else:
        # Run tests for a single optimizer
        result = run_single_optimizer_tests(base_dir, args.optimizer)
        return 0 if result and result.wasSuccessful() else 1


def clear_test_modules():
    """Clear test modules from sys.modules to avoid conflicts."""
    modules_to_remove = []
    for module_name in sys.modules:
        if (module_name.startswith('tests.') or 
            module_name.startswith('test_') or
            module_name == 'tests'):
            modules_to_remove.append(module_name)
    
    for module_name in modules_to_remove:
        del sys.modules[module_name]


def run_single_optimizer_tests(base_dir, optimizer):
    """Run tests for a single optimizer."""
    # Clear any cached test modules to avoid conflicts
    clear_test_modules()
    
    # Create a fresh test loader for each optimizer
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    test_count = 0
    
    if optimizer in ['mlb', 'all']:
        print(f"\nDiscovering MLB optimizer tests...")
        mlb_test_dir = os.path.join(base_dir, 'MLB_Optimizer', 'tests')
        if os.path.exists(mlb_test_dir):
            try:
                # Add the MLB_Optimizer directory to sys.path temporarily
                mlb_optimizer_dir = os.path.join(base_dir, 'MLB_Optimizer')
                if mlb_optimizer_dir not in sys.path:
                    sys.path.insert(0, mlb_optimizer_dir)
                
                mlb_tests = test_loader.discover(mlb_test_dir, pattern='test_*.py', top_level_dir=mlb_optimizer_dir)
                test_suite.addTest(mlb_tests)
                mlb_count = sum(1 for _ in mlb_tests)
                test_count += mlb_count
                print(f"Found {mlb_count} MLB test cases in {mlb_test_dir}")
                # List the test files found
                test_files = [os.path.basename(f) for f in os.listdir(mlb_test_dir) if f.startswith('test_') and f.endswith('.py')]
                print(f"MLB test files: {', '.join(test_files)}")
                
                # Remove from sys.path
                if mlb_optimizer_dir in sys.path:
                    sys.path.remove(mlb_optimizer_dir)
            except Exception as e:
                print(f"Error discovering MLB tests: {e}")
                print("Make sure MLB_Optimizer has all the required files.")
                # Remove from sys.path if there was an error
                if mlb_optimizer_dir in sys.path:
                    sys.path.remove(mlb_optimizer_dir)
        else:
            print(f"Warning: MLB test directory not found at {mlb_test_dir}")

    if optimizer in ['f1', 'all']:
        print(f"\nDiscovering F1 optimizer tests...")
        f1_test_dir = os.path.join(base_dir, 'F1_Optimizer', 'tests')
        if os.path.exists(f1_test_dir):
            try:
                # Add the F1_Optimizer directory to sys.path temporarily
                f1_optimizer_dir = os.path.join(base_dir, 'F1_Optimizer')
                if f1_optimizer_dir not in sys.path:
                    sys.path.insert(0, f1_optimizer_dir)
                
                f1_tests = test_loader.discover(f1_test_dir, pattern='test_*.py', top_level_dir=f1_optimizer_dir)
                test_suite.addTest(f1_tests)
                f1_count = sum(1 for _ in f1_tests)
                test_count += f1_count
                print(f"Found {f1_count} F1 test cases in {f1_test_dir}")
                # List the test files found
                test_files = [os.path.basename(f) for f in os.listdir(f1_test_dir) if f.startswith('test_') and f.endswith('.py')]
                print(f"F1 test files: {', '.join(test_files)}")
                
                # Remove from sys.path
                if f1_optimizer_dir in sys.path:
                    sys.path.remove(f1_optimizer_dir)
            except Exception as e:
                print(f"Error discovering F1 tests: {e}")
                print("Make sure F1_Optimizer has all the required files.")
                # Remove from sys.path if there was an error
                if f1_optimizer_dir in sys.path:
                    sys.path.remove(f1_optimizer_dir)
        else:
            print(f"Warning: F1 test directory not found at {f1_test_dir}")

    if optimizer in ['nba-wnba', 'all']:
        print(f"\nDiscovering NBA/WNBA Showdown Captain optimizer tests...")
        nba_wnba_test_dir = os.path.join(base_dir, 'NBA-WNBA-ShowdownCaptain_optimizer', 'tests')
        if os.path.exists(nba_wnba_test_dir):
            try:
                # Add the NBA-WNBA-ShowdownCaptain_optimizer directory to sys.path temporarily
                nba_wnba_optimizer_dir = os.path.join(base_dir, 'NBA-WNBA-ShowdownCaptain_optimizer')
                if nba_wnba_optimizer_dir not in sys.path:
                    sys.path.insert(0, nba_wnba_optimizer_dir)
                
                nba_wnba_tests = test_loader.discover(nba_wnba_test_dir, pattern='test_*.py', top_level_dir=nba_wnba_optimizer_dir)
                test_suite.addTest(nba_wnba_tests)
                nba_wnba_count = sum(1 for _ in nba_wnba_tests)
                test_count += nba_wnba_count
                print(f"Found {nba_wnba_count} NBA/WNBA test cases in {nba_wnba_test_dir}")
                # List the test files found
                test_files = [os.path.basename(f) for f in os.listdir(nba_wnba_test_dir) if f.startswith('test_') and f.endswith('.py')]
                print(f"NBA/WNBA test files: {', '.join(test_files)}")
                
                # Remove from sys.path
                if nba_wnba_optimizer_dir in sys.path:
                    sys.path.remove(nba_wnba_optimizer_dir)
            except Exception as e:
                print(f"Error discovering NBA/WNBA tests: {e}")
                print("Make sure NBA-WNBA-ShowdownCaptain_optimizer has all the required files.")
                # Remove from sys.path if there was an error
                if nba_wnba_optimizer_dir in sys.path:
                    sys.path.remove(nba_wnba_optimizer_dir)
        else:
            print(f"Warning: NBA/WNBA test directory not found at {nba_wnba_test_dir}")

    # Run the tests
    print(f"\nRunning {optimizer} tests...")
    print(f"Total test cases to run: {test_count}")
    print("-" * 70)
    
    if test_count == 0:
        print("No tests found to run.")
        return None
    
    start_time = datetime.datetime.now()
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    end_time = datetime.datetime.now()
    duration = end_time - start_time
    
    # Print test summary
    print(f"\n{optimizer.upper()} Test Summary:")
    print("-" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print(f"Test duration: {duration.total_seconds():.2f} seconds")
    
    if result.wasSuccessful():
        print(f"\n{optimizer.upper()} tests PASSED!")
    else:
        print(f"\n{optimizer.upper()} tests FAILED.")
        
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
    
    return result


if __name__ == '__main__':
    try:
        sys.exit(run_tests())
    except Exception as e:
        print(f"\nError running tests: {e}")
        sys.exit(1)
