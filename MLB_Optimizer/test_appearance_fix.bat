@echo off
setlocal

echo Testing optimizer with max-player-appearances...
echo.

set max_player_value=5
echo Using default value: %max_player_value%

python advanced_optimizer.py --auto-detect-injury --max-player-appearances %max_player_value% --num-lineups 1

echo.
echo Test complete. If this worked, we know the issue was with the validation logic.
echo.
pause
endlocal
