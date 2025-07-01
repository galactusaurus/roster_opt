# Troubleshooting Test Setup

If you're encountering issues with the test setup process, this guide offers solutions to common problems.

## Common Installation Issues

### Permission Errors

If you see errors like:

```
ERROR: Could not install packages due to an OSError: [WinError 2] The system cannot find the file specified
```

or

```
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

Try these solutions:

1. **Run as Administrator**: Right-click on `setup_tests.bat` and select "Run as administrator"

2. **Use the `--user` Flag**: The updated scripts now use this flag by default, which installs packages to your user directory instead of system directories.

3. **Manual Installation**: If automatic installation fails, install the required packages manually:

   ```
   python -m pip install pandas pulp numpy requests pytest coverage --user
   ```

### Alternative Setup Method

If you continue to have issues with the regular setup script, use `check_test_env.bat` instead:

1. Run `check_test_env.bat` to:
   - Check if required packages are already installed
   - Create necessary test directories
   - Provide manual installation instructions if packages are missing

2. After addressing any missing packages, you can run tests with `run_tests.bat`

## Running Tests With Missing Packages

If certain packages are missing but you want to run only the tests that don't require those packages:

1. Try running specific test files directly:

   ```
   python -m unittest MLB_Optimizer/tests/test_optimizer.py
   ```

2. Specify a particular optimizer to test:

   ```
   run_tests.bat mlb
   ```

   or

   ```
   run_tests.bat f1
   ```

## Creating Test Files Manually

If the test directories exist but are empty, you may need to manually copy the test files from your source code repository. Ensure each test directory has:

1. An `__init__.py` file (can be empty)
2. Test files (e.g., `test_optimizer.py`, `test_advanced_optimizer.py`, etc.)

## Virtual Environment Alternative

If you continue to have issues with package installation, consider creating a virtual environment:

```
python -m venv test_env
test_env\Scripts\activate
python -m pip install pandas pulp numpy requests pytest coverage
```

Then run tests within this environment.
