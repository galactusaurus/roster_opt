@echo off
setlocal enabledelayedexpansion

echo Testing option 4 in isolation...
echo.

:: Set a hard-coded value
set max_player_value=1

echo Using max player appearances: !max_player_value!
echo.

echo Running optimizer with hard-coded value...
python advanced_optimizer.py --auto-detect-injury --output "test_output.csv" --max-player-appearances !max_player_value!

echo.
echo Test complete.
pause
endlocal
