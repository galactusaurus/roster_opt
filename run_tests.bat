@echo off
echo Running roster optimizer test suite
echo ===============================
echo.

REM Check if python is available
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in the PATH
    exit /b 1
)

REM Parse command line arguments
set optimizer_arg=all
if not "%1"=="" (
    if "%1"=="mlb" set optimizer_arg=mlb
    if "%1"=="f1" set optimizer_arg=f1
    if "%1"=="all" set optimizer_arg=all
)

REM Create test_results directory if it doesn't exist
if not exist "test_results" mkdir test_results

REM Generate timestamp for the output file
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YYYY=%dt:~0,4%"
set "MM=%dt:~4,2%"
set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%"
set "Min=%dt:~10,2%"
set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"

REM Set the output file path
set "output_file=test_results\test_results_%timestamp%.txt"

REM Run the tests with the specified argument and redirect output to file
echo Running tests for: %optimizer_arg%
echo Results will be saved to: %output_file%
echo.
echo Test run started at %time% on %date% > "%output_file%"
echo Optimizer: %optimizer_arg% >> "%output_file%"
echo ======================================== >> "%output_file%"
echo. >> "%output_file%"

REM Run tests and capture output
python run_tests.py --optimizer %optimizer_arg% >> "%output_file%" 2>&1

REM Check if tests succeeded
set test_exit_code=%errorlevel%
echo. >> "%output_file%"
echo Test run completed at %time% on %date% >> "%output_file%"

if %test_exit_code% neq 0 (
    echo ======================================== >> "%output_file%"
    echo Tests FAILED with errors. >> "%output_file%"
    echo.
    echo Tests failed with errors.
    echo See detailed results in: %output_file%
    exit /b 1
) else (
    echo ======================================== >> "%output_file%"
    echo All tests PASSED successfully! >> "%output_file%"
    echo.
    echo All tests passed successfully!
    echo See detailed results in: %output_file%
)

pause
