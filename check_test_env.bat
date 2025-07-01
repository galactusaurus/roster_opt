@echo off
echo Alternative Setup for Test Environment
echo ===================================
echo.

echo This script will check if required packages are available without attempting to install them.
echo If packages are missing, it will provide instructions for manual installation.
echo.

REM Check if python is available
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in the PATH
    echo Please make sure Python is installed and added to your PATH environment variable.
    pause
    exit /b 1
)

echo Checking required packages...
echo.

setlocal EnableDelayedExpansion
set all_packages_available=true

REM Check each required package
for %%p in (pandas pulp numpy requests pytest coverage) do (
    python -c "import %%p" 2>nul
    if !errorlevel! neq 0 (
        echo Package %%p is not available.
        set all_packages_available=false
    ) else (
        echo Package %%p is installed.
    )
)

echo.
if "%all_packages_available%"=="true" (
    echo All required packages are available!
) else (
    echo Some required packages are missing.
    echo.
    echo Please install the missing packages manually using:
    echo python -m pip install pandas pulp numpy requests pytest coverage --user
    echo.
    echo After installation, run this script again to verify all packages are available.
)

echo.
echo Setting up test directories...
if not exist "MLB_Optimizer\tests" mkdir "MLB_Optimizer\tests"
if not exist "F1_Optimizer\tests" mkdir "F1_Optimizer\tests"

echo.
echo Directory setup complete!
echo.
echo If all packages are installed, you can run the tests with:
echo   run_tests.bat
echo.

pause
