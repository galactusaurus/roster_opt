@echo off
echo NBA/WNBA Showdown Captain Lineup Optimizer
echo ========================================
echo.
echo Please select an option:
echo 1. Copy latest DraftKings file from Downloads
echo 2. Run optimizer with existing file
echo 3. Exit
echo.

set /p option="Enter your choice (1-3): "

if "%option%"=="1" (
    echo.
    echo Copying latest DraftKings file...
    python copy_dk_file.py
    echo.
    pause
    goto :eof
)

if "%option%"=="2" (
    goto run_optimizer
)

if "%option%"=="3" (
    echo Exiting...
    goto :eof
)

echo Invalid option. Please try again.
pause
goto :eof

:run_optimizer

REM Check if a data file was provided
if "%1"=="" (
    set "data_file=DKSalaries.csv"
) else (
    set "data_file=%1"
)

REM Check if file exists
if not exist "%data_file%" (
    echo Error: Data file '%data_file%' not found.
    echo Please download a DraftKings salary file and save it as DKSalaries.csv
    echo or specify the path to your data file as an argument.
    goto :end
)

REM Get number of lineups
set "num_lineups=10"
if not "%2"=="" (
    set "num_lineups=%2"
)

REM Get optional team stack
set "stack_team="
if not "%3"=="" (
    set "stack_team=%3"
)

REM Run the optimizer
echo Running optimizer with:
echo - Data file: %data_file%
echo - Number of lineups: %num_lineups%
if not "%stack_team%"=="" (
    echo - Team stack: %stack_team%
    python advanced_optimizer.py "%data_file%" %num_lineups% %stack_team%
) else (
    echo - No team stack specified
    python advanced_optimizer.py "%data_file%" %num_lineups%
)

echo.
echo Optimization complete.

:end
pause
