@echo off
echo Formula 1 DFS Lineup Optimizer
echo ============================
echo.
echo Please select an option:
echo 1. Run basic optimizer
echo 2. Run advanced optimizer
echo 3. Exit
echo.

set /p option="Enter your choice (1-3): "

if "%option%"=="1" (
    echo.
    echo Running basic Formula 1 lineup optimizer...
    echo.
    python optimizer.py
    pause
    exit /b 0
)

if "%option%"=="2" (
    echo.
    echo Running advanced Formula 1 lineup optimizer...
    echo.
    python advanced_optimizer.py
    pause
    exit /b 0
)

if "%option%"=="3" (
    echo Exiting...
    exit /b 0
)

echo Invalid option. Please try again.
pause
exit /b 1
