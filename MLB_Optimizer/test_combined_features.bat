@echo off
echo Testing Combined Features: Injury Filtering and Player Appearance Limits
echo =====================================================================
echo.
echo This batch file demonstrates how to use both injury filtering and player
echo appearance limits together to optimize your MLB lineups.
echo.

echo Running the MLB optimizer with both injury filtering and player appearance limits...
echo.
echo The optimizer will automatically search for the most recent injury file.
echo.

if "%FOUND_INJURY_FILE%"=="0" (
    echo No injury file found. Please download or create an MLB injury report file.
    echo.
    echo Would you like to:
    echo 1. Continue without injury filtering
    echo 2. Specify an injury file path
    echo 3. Exit
    
    set /p choice="Enter choice (1-3): "
    
    if "%choice%"=="1" (
        set /p num_lineups="Enter number of lineups to generate: "
        set /p max_appearances="Enter maximum appearances per player: "
        
        echo.
        echo Running optimizer with player appearance limits only...
        python advanced_optimizer.py --num-lineups %num_lineups% --max-player-appearances %max_appearances%
    ) else if "%choice%"=="2" (
        set /p custom_injury="Enter path to injury file: "
        if exist "%custom_injury%" (
            set /p num_lineups="Enter number of lineups to generate: "
            set /p max_appearances="Enter maximum appearances per player: "
            
            echo.
            echo Running optimizer with both injury filtering and player appearance limits...
            python advanced_optimizer.py --injured-list "%custom_injury%" --num-lineups %num_lineups% --max-player-appearances %max_appearances%
        ) else (
            echo Error: File not found. Exiting...
        )
    ) else (
        echo Exiting script...
    )
) else (
    echo.
    echo Last modified:
    for /f "tokens=1,2" %%a in ('PowerShell -Command "Get-Item \"%INJURY_FILE%\" | Select-Object -ExpandProperty LastWriteTime"') do echo %%a %%b
    echo.
    
    set /p num_lineups="Enter number of lineups to generate: "
    set /p max_appearances="Enter maximum appearances per player: "
    
    echo.
    echo Running optimizer with both injury filtering and player appearance limits...
    python advanced_optimizer.py --injured-list "%INJURY_FILE%" --num-lineups=%num_lineups% --max-player-appearances=%max_appearances%
)

echo.
echo Optimization complete!
pause
