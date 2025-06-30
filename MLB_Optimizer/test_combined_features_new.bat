@echo off
echo Testing Combined Features: Injury Filtering and Player Appearance Limits
echo =====================================================================
echo.
echo This batch file demonstrates how to use both injury filtering and player
echo appearance limits together to optimize your MLB lineups.
echo.
echo The optimizer will now automatically search for the most recent injury file.
echo.

set /p num_lineups="Enter number of lineups to generate: "
set /p max_appearances="Enter maximum appearances per player: "

echo.
echo Running MLB lineup optimizer with both auto-detected injury filtering and player appearance limits...
python advanced_optimizer.py --auto-detect-injury --num-lineups %num_lineups% --max-player-appearances %max_appearances%

echo.
echo Optimization complete!
pause
