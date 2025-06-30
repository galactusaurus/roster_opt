@echo off
setlocal enabledelayedexpansion
mode con: cols=100 lines=35
color 0A

:: MLB Optimizer Dashboard
:start
cls
echo +======================================================================================+
echo ^|                          MLB DAILY FANTASY LINEUP OPTIMIZER                          ^|
echo +======================================================================================+
echo ^|                                                                                      ^|
echo ^|  Select an option:                                                                   ^|
echo ^|                                                                                      ^|
echo ^|  [1] - Quick Optimize           - Generate standard lineups                          ^|
echo ^|  [2] - Advanced Optimize        - Use stacking and diversity features                ^|
echo ^|  [3] - Injury-Aware Optimize    - Auto-detect and filter out injured players         ^|
echo ^|  [4] - Full Optimize            - Combine injury filtering and appearance limits     ^|
echo ^|  [5] - Team Stack Optimize      - Focus on players from specific teams               ^|
echo ^|  [6] - Custom Optimize          - Configure all optimizer parameters                 ^|
echo ^|                                                                                      ^|
echo ^|  [7] - File Management          - Copy/find DraftKings and injury files              ^|
echo ^|  [8] - Help/Documentation       - Show detailed help information                     ^|
echo ^|  [9] - Exit                     - Exit the optimizer                                 ^|
echo ^|                                                                                      ^|
echo +======================================================================================+
echo.

set /p choice="Enter your choice (1-9): "

if "%choice%"=="1" goto quick_optimize
if "%choice%"=="2" goto advanced_optimize
if "%choice%"=="3" goto injury_optimize
if "%choice%"=="4" goto full_optimize
if "%choice%"=="5" goto stack_optimize
if "%choice%"=="6" goto custom_optimize
if "%choice%"=="7" goto file_management
if "%choice%"=="8" goto help_docs
if "%choice%"=="9" goto exit
echo Invalid choice. Please try again.
timeout /t 2 >nul
goto start

:quick_optimize
cls
echo +======================================================================================+
echo ^|                                 QUICK OPTIMIZE                                       ^|
echo +======================================================================================+
echo.
echo This option generates standard lineups using default settings.
echo.
set /p num_lineups="Enter number of lineups to generate [10]: "
if "!num_lineups!"=="" set num_lineups=10
echo.
echo Running optimizer to generate !num_lineups! lineups...
echo.
python advanced_optimizer.py --num-lineups !num_lineups!
echo.
echo Press any key to return to main menu...
pause >nul
goto start

:advanced_optimize
cls
echo +======================================================================================+
echo ^|                                ADVANCED OPTIMIZE                                     ^|
echo +======================================================================================+
echo.
set /p num_lineups="Enter number of lineups to generate [10]: "
if "!num_lineups!"=="" set num_lineups=10
set /p lineup_diversity="Enter minimum diversity between lineups [3]: "
if "!lineup_diversity!"=="" set lineup_diversity=3
echo.
echo Running advanced optimizer with lineup diversity settings...
echo.
python advanced_optimizer.py --num-lineups !num_lineups! --lineup-diversity !lineup_diversity!
echo.
echo Press any key to return to main menu...
pause >nul
goto start

:injury_optimize
cls
echo +======================================================================================+
echo ^|                              INJURY-AWARE OPTIMIZE                                   ^|
echo +======================================================================================+
echo.
echo This option automatically detects and uses the most recent injury list file.
echo.
set /p num_lineups="Enter number of lineups to generate [10]: "
if "!num_lineups!"=="" set num_lineups=10
echo.
echo Running optimizer with automatic injury detection...
echo.
python advanced_optimizer.py --auto-detect-injury --num-lineups !num_lineups!
echo.
echo Press any key to return to main menu...
pause >nul
goto start

:full_optimize
cls
echo +======================================================================================+
echo ^|                                 FULL OPTIMIZE                                        ^|
echo +======================================================================================+
echo.
echo This option combines automatic injury detection with player appearance limits.
echo.
set /p num_lineups="Enter number of lineups to generate [10]: "
if "!num_lineups!"=="" set num_lineups=10
set /p max_appearances="Enter maximum player appearances across lineups [4]: "
if "!max_appearances!"=="" set max_appearances=4
set /p lineup_diversity="Enter minimum diversity between lineups [3]: "
if "!lineup_diversity!"=="" set lineup_diversity=3
echo.
echo Running full optimizer with injury detection and appearance limits...
echo.
python advanced_optimizer.py --auto-detect-injury --num-lineups !num_lineups! --max-player-appearances !max_appearances! --lineup-diversity !lineup_diversity!
echo.
echo Press any key to return to main menu...
pause >nul
goto start

:stack_optimize
cls
echo +======================================================================================+
echo ^|                               TEAM STACK OPTIMIZE                                    ^|
echo +======================================================================================+
echo.
set /p num_lineups="Enter number of lineups to generate [10]: "
if "!num_lineups!"=="" set num_lineups=10
set /p stack_team="Enter team abbreviation to stack (e.g., HOU, NYY): "
set /p stack_count="Enter number of players from stacked team [4]: "
if "!stack_count!"=="" set stack_count=4
set /p use_injuries="Use injury detection? (y/n) [y]: "
if "!use_injuries!"=="" set use_injuries=y
echo.
echo Running optimizer with team stacking...
echo.

if /i "!use_injuries!"=="y" (
    python advanced_optimizer.py --num-lineups !num_lineups! --stack-team !stack_team! --stack-count !stack_count! --auto-detect-injury
) else (
    python advanced_optimizer.py --num-lineups !num_lineups! --stack-team !stack_team! --stack-count !stack_count!
)
echo.
echo Press any key to return to main menu...
pause >nul
goto start

:custom_optimize
cls
echo +======================================================================================+
echo ^|                               CUSTOM OPTIMIZE                                        ^|
echo +======================================================================================+
echo.
echo This option allows you to configure all optimizer parameters.
echo.
set /p num_lineups="Enter number of lineups to generate [10]: "
if "!num_lineups!"=="" set num_lineups=10
set /p stack_team="Enter team abbreviation to stack (leave blank for none): "
set stack_param=
if not "!stack_team!"=="" (
    set /p stack_count="Enter number of players from stacked team [4]: "
    if "!stack_count!"=="" set stack_count=4
    set stack_param=--stack-team !stack_team! --stack-count !stack_count!
)
set /p max_from_team="Enter maximum players from a single team [5]: "
if "!max_from_team!"=="" set max_from_team=5
set /p min_teams="Enter minimum number of teams in lineup [3]: "
if "!min_teams!"=="" set min_teams=3
set /p lineup_diversity="Enter minimum diversity between lineups [3]: "
if "!lineup_diversity!"=="" set lineup_diversity=3
set /p use_injuries="Use injury detection? (y/n) [y]: "
if "!use_injuries!"=="" set use_injuries=y
set /p max_appearances="Enter maximum player appearances (leave blank for no limit): "
set appearances_param=
if not "!max_appearances!"=="" (
    set appearances_param=--max-player-appearances !max_appearances!
)
echo.
echo Running custom optimizer...
echo.

set cmd=python advanced_optimizer.py --num-lineups !num_lineups! --max-from-team !max_from_team! --min-teams !min_teams! --lineup-diversity !lineup_diversity! !stack_param! !appearances_param!

if /i "!use_injuries!"=="y" (
    set cmd=!cmd! --auto-detect-injury
)

echo Executing: !cmd!
echo.
!cmd!

echo.
echo Press any key to return to main menu...
pause >nul
goto start

:file_management
cls
echo +======================================================================================+
echo ^|                                FILE MANAGEMENT                                       ^|
echo +======================================================================================+
echo.
echo [1] - Copy latest DraftKings file from Downloads
echo [2] - Search for injury files
echo [3] - Return to main menu
echo.
set /p file_choice="Enter your choice (1-3): "

if "!file_choice!"=="1" (
    python copy_dk_file.py
    echo.
    echo Press any key to return to file management...
    pause >nul
    goto file_management
)

if "!file_choice!"=="2" (
    echo Searching for injury files...
    echo.
    python -c "from advanced_optimizer import find_injured_list; find_injured_list()"
    echo.
    echo Press any key to return to file management...
    pause >nul
    goto file_management
)

if "!file_choice!"=="3" goto start

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto file_management

:help_docs
cls
echo +======================================================================================+
echo ^|                             HELP & DOCUMENTATION                                     ^|
echo +======================================================================================+
echo.
echo MLB Daily Fantasy Lineup Optimizer Help
echo.
echo This tool optimizes DraftKings lineups for MLB contests using linear programming.
echo.
echo Key Features:
echo  - Automatic injury detection - finds and uses the most recent injury list file
echo  - Player appearance limits - control how many times a player appears across lineups
echo  - Team stacking - strategically select multiple players from the same team
echo  - Lineup diversity - ensure variety between generated lineups
echo.
echo Recommended Workflow:
echo  1. Use "Copy latest DraftKings file" to get the latest contest data
echo  2. Run "Full Optimize" for best results with injury filtering and appearance limits
echo  3. Review the generated lineups in the "Outputs" folder
echo.
echo Injury Files:
echo  - The optimizer will automatically find the most recent injury CSV file
echo  - Files should have "injury", "injured", or "IL" in the filename
echo  - The file should contain player names in a column named "Name" or similar
echo.
echo Press any key to return to main menu...
pause >nul
goto start

:exit
cls
echo Thank you for using the MLB Daily Fantasy Lineup Optimizer!
echo.
echo Exiting...
timeout /t 2 >nul
exit /b 0
