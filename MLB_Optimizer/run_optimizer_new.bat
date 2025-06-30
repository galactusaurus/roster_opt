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
echo 4. Run Advanced Optimizer with Injury List AND Appearance Limits
echo 5. Copy DraftKings file from Downloads
echo 6. Return to Main Menu
echo.

set /p choice="Enter your choice (1-6): "

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
        :: Enable delayed expansion for variables inside the code block
        setlocal enabledelayedexpansion
        
        :: Set default first, then get user input
        set player_limit=5
        set /p player_limit="Enter the maximum number of lineups a player can appear in (or press Enter for default 5): "
        
        :: Debug info - show the exact value captured
        echo Value entered: [!player_limit!]
        
        :: If they just pressed Enter, use the default that was already set
        if "!player_limit!"=="" (
            echo Using default maximum of 5 appearances per player.
            set player_limit=5
        )
        
        echo.
        echo Max player appearances: !player_limit!
        python advanced_optimizer.py --output "optimized_lineups.csv" --max-player-appearances !player_limit!
        
        :: End the local scope
        endlocal
    ) else (
        python advanced_optimizer.py --output "optimized_lineups.csv"
    )
    
    pause
    goto menu
)

if "%choice%"=="3" (
    echo Looking for MLB injury list CSV files...
    echo.
    
    echo Running optimizer with automatic injury file detection...
    python advanced_optimizer.py --auto-detect-injury --output "optimized_lineups.csv"
    
    pause
    goto menu
)

if "%choice%"=="4" (
    echo Running Advanced Optimizer with Injury List AND Appearance Limits...
    echo.
    echo The optimizer will automatically search for the most recent injury file.
    echo.
    
    :: Enable delayed expansion for variables inside the code block
    setlocal enabledelayedexpansion
    
    :: Set default first, then get user input
    set player_limit=5
    set /p player_limit="Enter the maximum number of lineups a player can appear in (or press Enter for default 5): "
    
    :: Debug info - show the exact value captured
    echo Value entered: [!player_limit!]
    
    :: If they just pressed Enter, use the default that was already set
    if "!player_limit!"=="" (
        echo Using default maximum of 5 appearances per player.
        set player_limit=5
    )
    
    echo.
    echo Running optimizer with both injury filtering and player appearance limits...
    echo Max player appearances: !player_limit!
    
    python advanced_optimizer.py --auto-detect-injury --output "optimized_lineups.csv" --max-player-appearances !player_limit!
    
    :: End the local scope
    endlocal
    
    pause
    goto menu
)

if "%choice%"=="5" (
    echo Copying DraftKings file from Downloads...
    python copy_dk_file.py
    pause
    goto menu
)

if "%choice%"=="6" (
    echo Returning to main menu...
    exit /b
) else (
    if not "%choice%"=="1" if not "%choice%"=="2" if not "%choice%"=="3" if not "%choice%"=="4" if not "%choice%"=="5" if not "%choice%"=="6" (
        echo Invalid option. Please try again.
        pause
        goto menu
    )
)
