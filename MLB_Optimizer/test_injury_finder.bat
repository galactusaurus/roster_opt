@echo off
echo Testing injury list finder...
echo.
if exist "c:\git\roster_opt\mlb-injury-report.csv" (
    echo Latest injury file found: c:\git\roster_opt\mlb-injury-report.csv
) else (
    python -c "import os, glob, sys; all_files = []; paths = [os.getcwd(), os.path.dirname(os.getcwd()), os.path.join(os.path.expanduser('~'), 'Downloads'), r'c:\git\roster_opt']; patterns = ['mlb-injury*.csv', '*injury*.csv', '*injured*.csv', '*-IL-*.csv']; [all_files.extend(glob.glob(os.path.join(p, pat))) for p in paths for pat in patterns]; all_files.sort(key=lambda x: os.path.getmtime(x), reverse=True); print('Latest injury file found: ' + (all_files[0] if all_files else 'None'));"
)

echo.
echo Test complete.
pause
