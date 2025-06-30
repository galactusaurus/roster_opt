@echo off
echo MLB Daily Fantasy Lineup Optimizer
echo ================================
echo.

:menu
echo Select an option:
echo.
echo 1. Run Basic Optimizer
echo 2. Run Advanced Optimizer
echo 3. Run Advanced Optimizer with Injury List
echo 4. Copy DraftKings file from Downloads
echo 5. Return to Main Menu
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo Running basic optimizer...
    python optimizer.py
    pause
    goto menu
)

if "%choice%"=="2" (
    echo Running advanced optimizer...
    
    :: Ask about lineup differentiation
    set /p use_diff="Do you want to limit the number of times a player can appear in lineups? (y/n): "
    
    if /i "%use_diff%"=="y" (
        set /p max_appearances="Enter the maximum number of lineups a player can appear in: "
        echo.
        python advanced_optimizer.py --output "optimized_lineups.csv" --max-player-appearances %max_appearances%
    ) else (
        python advanced_optimizer.py --output "optimized_lineups.csv"
    )
    
    pause
    goto menu
)

if "%choice%"=="3" (
    echo Looking for MLB injury list CSV files...
    echo.
    
    :: First check for the injury report in standard locations
    set FOUND_INJURY_FILE=0
    
    :: Check project root directory first (most common)
    if exist "..\mlb-injury-report.csv" (
        set INJURY_FILE=..\mlb-injury-report.csv
        set FOUND_INJURY_FILE=1
        echo Found injury file: %INJURY_FILE%
    )
    
    :: If not found in project root, search other locations
    if "%FOUND_INJURY_FILE%"=="0" (
        for /f "delims=" %%i in ('python -c "import os, glob, sys; all_files = []; paths = [os.getcwd(), os.path.dirname(os.getcwd()), os.path.join(os.path.expanduser('~'), 'Downloads')]; patterns = ['mlb-injury*.csv', '*injury*.csv', '*injured*.csv', '*-IL-*.csv']; [all_files.extend(glob.glob(os.path.join(p, pat))) for p in paths for pat in patterns]; all_files.sort(key=lambda x: os.path.getmtime(x), reverse=True); print(all_files[0] if all_files else '')"') do (
            if not "%%i"=="" (
                set INJURY_FILE=%%i
                set FOUND_INJURY_FILE=1
                echo Found injury file: %%i
            )
        )
    )
    
    if "%FOUND_INJURY_FILE%"=="1" (
        echo.
        echo Last modified:
        for /f "tokens=1,2" %%a in ('PowerShell -Command "Get-Item '%INJURY_FILE%' | Select-Object -ExpandProperty LastWriteTime"') do echo %%a %%b
        echo.
        set /p USE_FILE="Use this injury list? (y/n): "
        
        if /i "%USE_FILE%"=="y" (
            :: Ask about lineup differentiation
            set /p use_diff="Do you want to limit the number of times a player can appear in lineups? (y/n): "
            
            if /i "%use_diff%"=="y" (
                set /p max_appearances="Enter the maximum number of lineups a player can appear in: "
                echo.
                python advanced_optimizer.py --injured-list "%INJURY_FILE%" --output "optimized_lineups.csv" --max-player-appearances %max_appearances%
            ) else (
                python advanced_optimizer.py --injured-list "%INJURY_FILE%" --output "optimized_lineups.csv"
            )
        ) else (
            echo Running without injury list filter.
            
            :: Ask about lineup differentiation
            set /p use_diff="Do you want to limit the number of times a player can appear in lineups? (y/n): "
            
            if /i "%use_diff%"=="y" (
                set /p max_appearances="Enter the maximum number of lineups a player can appear in: "
                echo.
                python advanced_optimizer.py --output "optimized_lineups.csv" --max-player-appearances %max_appearances%
            ) else (
                python advanced_optimizer.py --output "optimized_lineups.csv"
            )
        )
    ) else (
        echo No injury list found automatically.
        set /p CUSTOM_FILE="Enter path to injury list CSV (or press Enter to skip): "
        
        if not "%CUSTOM_FILE%"=="" (
            python advanced_optimizer.py --injured-list "%CUSTOM_FILE%" --output "optimized_lineups.csv"
        ) else (
            echo Running without injury list filter.
            python advanced_optimizer.py --output "optimized_lineups.csv"
        )
    )
    
    pause
    goto menu
)

if "%choice%"=="4" (
    echo Copying DraftKings file from Downloads...
    python copy_dk_file.py
    pause
    goto menu
)

if "%choice%"=="5" (
    echo Returning to main menu...
    exit /b
) else (
    if not "%choice%"=="1" if not "%choice%"=="2" if not "%choice%"=="3" if not "%choice%"=="4" (
        echo Invalid option. Please try again.
        pause
        goto menu
    )
)
