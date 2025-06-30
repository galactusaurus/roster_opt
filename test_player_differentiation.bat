@echo off
echo Testing Player Differentiation Feature
echo =====================================
echo.
echo This batch file demonstrates how to use the player differentiation feature 
echo to limit the number of times a player can appear in your optimized lineups.
echo.
echo The optimizer will show:
echo  1. Which players were excluded from each lineup due to max appearance limits
echo  2. A summary of player usage across all lineups when finished
echo.

set /p sport="Select sport (1=MLB, 2=F1): "
set /p num_lineups="Enter number of lineups to generate: "
set /p max_appearances="Enter maximum appearances per player: "

if "%sport%"=="1" (
    echo.
    echo Running MLB optimizer with max %max_appearances% appearances per player...
    echo.
    cd MLB_Optimizer
    python advanced_optimizer.py --num-lineups %num_lineups% --max-player-appearances %max_appearances%
    cd ..
) else if "%sport%"=="2" (
    echo.
    echo Running Formula 1 optimizer with max %max_appearances% appearances per player...
    echo.
    cd F1_Optimizer
    python advanced_optimizer.py --num-lineups %num_lineups% --max-player-appearances %max_appearances%
    cd ..
) else (
    echo Invalid sport selection
)

echo.
echo Test complete!
pause
