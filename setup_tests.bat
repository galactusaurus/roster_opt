@echo off
echo Setting up test environment for roster optimizers
echo ==============================================
echo.

REM Check if python is available
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in the PATH
    echo Please make sure Python is installed and added to your PATH environment variable.
    pause
    exit /b 1
)

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% equ 0 (
    echo Running with administrator privileges.
) else (
    echo Note: Not running as administrator. If you encounter permission errors,
    echo try running this script as administrator by right-clicking and selecting
    echo "Run as administrator".
    echo.
)

echo Installing requirements and setting up test directories...
python setup_tests.py

if %errorlevel% neq 0 (
    echo.
    echo Warning: Setup script returned an error code.
    echo Some packages might not have been installed correctly.
    echo.
    echo If you encounter issues running the tests, try the following:
    echo 1. Run this script as administrator
    echo 2. Manually install requirements with:
    echo    python -m pip install pandas pulp numpy requests pytest coverage --user
    echo.
    echo Press any key to continue anyway...
    pause
)

echo.
echo Setup process completed!
echo.
echo You can now run the tests with:
echo   run_tests.bat
echo.

pause
