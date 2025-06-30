@echo off
echo Running combined optimizer...
echo.

:: Check for valid input - must be a number
set value=%1
if "%value%"=="" set value=5

:: Ensure it's a number by checking if it's purely digits
echo %value%|findstr /r "^[0-9][0-9]*$" >nul
if errorlevel 1 (
    echo Invalid input - using default value of 5
    set value=5
)

echo Using max appearances: %value%

python advanced_optimizer.py --auto-detect-injury --output "optimized_lineups.csv" --max-player-appearances %value%
echo.
