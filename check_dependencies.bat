@echo off
echo Checking required dependencies for roster optimizer tests
echo ===================================================
echo.

python check_dependencies.py

if %errorlevel% neq 0 (
    echo.
    echo Please install the missing packages before running the tests.
    echo.
)

pause
