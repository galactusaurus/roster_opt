@echo off
echo Setting up WNBA Showdown Lineup Optimizer
echo ========================================

REM Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in your PATH
    echo Please install Python 3.7+ from https://www.python.org/downloads/
    goto :end
)

echo Installing required packages...
pip install pandas numpy pulp

echo Creating Outputs directory...
if not exist "Outputs" mkdir Outputs

echo.
echo Setup complete!
echo.
echo To run the optimizer:
echo - Place your DraftKings salary file (DKSalaries.csv) in this directory
echo - Run 'run_optimizer.bat' to generate lineups
echo.
echo For more options, see the README.md file.

:end
pause
