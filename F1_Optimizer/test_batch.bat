@echo off
echo Running Formula 1 Advanced Optimizer with test parameters...
echo.

REM Find the latest DKSalaries file and use it for the test
python copy_dk_file.py

echo.
echo Running advanced optimizer with test settings...
python advanced_optimizer.py --num-lineups 5 --stack-team MCL --stack-count 2 --max-from-team 2 --min-teams 3

echo.
echo Test completed.
pause
