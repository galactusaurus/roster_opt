@echo off
echo Daily Fantasy Sports Lineup Optimizer
echo ====================================
echo.

:menu
echo Choose a sport league to optimize:
echo.
echo 1. MLB (Baseball)
echo 2. Formula 1
echo 3. NBA/WNBA Showdown Captain
echo 4. NFL (Football) - Coming soon
echo 5. NHL (Hockey) - Coming soon
echo 6. Exit
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" (
    cd MLB_Optimizer
    call run_optimizer.bat
    cd ..
    goto menu
)

if "%choice%"=="2" (
    cd F1_Optimizer
    call run_optimizer.bat
    cd ..
    goto menu
)

if "%choice%"=="3" (
    cd NBA-WNBA-ShowdownCaptain_optimizer
    call run_optimizer.bat
    cd ..
    goto menu
)

if "%choice%"=="4" (
    echo NFL optimization is not yet available.
    echo This feature will be implemented soon!
    echo.
    pause
    goto menu
)

if "%choice%"=="5" (
    echo NHL optimization is not yet available.
    echo This feature will be implemented soon!
    echo.
    pause
    goto menu
)

if "%choice%"=="6" (
    echo Thanks for using Daily Fantasy Sports Lineup Optimizer!
    goto :eof
) else (
    echo Invalid choice. Please try again.
    pause
    cls
    goto menu
)
