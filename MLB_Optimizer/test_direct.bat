@echo off
setlocal enabledelayedexpansion

echo Testing appearance limit directly...
echo.

set /p appearances="Enter max appearances (Any positive number): "

:: Check if input is empty - use default if it is
if "!appearances!"=="" (
    set appearances=5
    echo Using default value of 5.
)

:: Debug output
echo Value entered: [!appearances!]

echo Running optimizer with max-player-appearances=!appearances!
python advanced_optimizer.py --auto-detect-injury --max-player-appearances !appearances! --num-lineups 3

echo.
if %errorlevel% NEQ 0 (
    echo Error detected. The optimizer did not run successfully.
) else (
    echo Optimizer completed successfully.
)

pause
endlocal
