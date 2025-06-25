@echo off
echo Setting up Formula 1 DFS Lineup Optimizer...
echo.

REM Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.6 or higher.
    echo Visit https://www.python.org/downloads/ to download Python.
    pause
    exit /b 1
)

echo Installing required packages...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Failed to install required packages. Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo Setup completed successfully!
echo.
echo You can now run the optimizer using:
echo   - python optimizer.py (basic version)
echo   - python advanced_optimizer.py (advanced version)
echo.
echo Make sure to download the latest DraftKings salaries CSV file before running.
echo.
pause
