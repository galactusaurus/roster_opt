@echo off
echo Daily Fantasy Sports Lineup Optimizer
echo ====================================
echo.

:menu
echo Choose a sport league to optimize:
echo.
echo 1. MLB (Baseball)
echo 2. NFL (Football) - Coming soon
echo 3. NBA (Basketball) - Coming soon
echo 4. NHL (Hockey) - Coming soon
echo 5. Exit
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    cd MLB_Optimizer
    call run_optimizer.bat
    cd ..
    goto menu
)

if "%choice%"=="2" (
    echo NFL optimization is not yet available.
    echo This feature will be implemented soon!
    echo.
    pause
    goto menu
)

if "%choice%"=="3" (
    echo NBA optimization is not yet available.
    echo This feature will be implemented soon!
    echo.
    pause
    goto menu
)

if "%choice%"=="4" (
    echo NHL optimization is not yet available.
    echo This feature will be implemented soon!
    echo.
    pause
    goto menu
)

if "%choice%"=="5" (
    echo Thanks for using Daily Fantasy Sports Lineup Optimizer!
    goto :eof
) else (
    echo Invalid choice. Please try again.
    pause
    cls
    goto menu
)
