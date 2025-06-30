@echo off
setlocal enabledelayedexpansion

echo Testing input handling...
echo.

:: Method 1: Direct input with default re-setting
set max_appearances=5
set /p max_appearances="Method 1 - Enter a number [5]: "
if "!max_appearances!"=="" (
    set max_appearances=5
)
echo Method 1 result: !max_appearances!
echo.

:: Method 2: Using intermediate variable
set appearances=5
set /p input="Method 2 - Enter a number [5]: "
if defined input (
    set appearances=!input!
)
echo Method 2 result: !appearances!
echo.

:: Method 3: Direct with delayed expansion
set value=5
set /p value="Method 3 - Enter a number [5]: "
echo Method 3 result: !value!
echo.

echo All done - check which method worked correctly.
pause
endlocal
