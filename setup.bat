@echo off
echo Setting up Daily Fantasy Sports Lineup Optimizer...

echo.
echo Installing required Python packages for all optimizers...

cd MLB_Optimizer
echo Installing MLB Optimizer packages...
pip install -r requirements.txt
cd ..

cd F1_Optimizer
echo Installing Formula 1 Optimizer packages...
pip install -r requirements.txt
cd ..

rem Future extensions can be added here
rem cd NFL_Optimizer
rem echo Installing NFL Optimizer packages...
rem pip install -r requirements.txt
rem cd ..

echo.
echo Setup complete! You can now run the optimizer by executing optimize.bat
echo.
