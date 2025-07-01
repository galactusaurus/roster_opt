@echo off
echo Testing WNBA Showdown Optimizer
echo =============================

REM Create a small test dataset for validation
echo Creating test data...
echo Position,Name + ID,Name,ID,Roster Position,Salary,Game Info,TeamAbbrev,AvgPointsPerGame > test_data.csv
echo G,Sabrina Ionescu (12345),Sabrina Ionescu,12345,CPT,10000,LVA@NYL,NYL,45.2 >> test_data.csv
echo G,Jackie Young (23456),Jackie Young,23456,UTIL,9500,LVA@NYL,LVA,42.5 >> test_data.csv
echo F,A'ja Wilson (34567),A'ja Wilson,34567,UTIL,11000,LVA@NYL,LVA,50.8 >> test_data.csv
echo F,Breanna Stewart (45678),Breanna Stewart,45678,UTIL,10500,NYL@CON,NYL,49.3 >> test_data.csv
echo G,Chelsea Gray (56789),Chelsea Gray,56789,UTIL,8000,LVA@NYL,LVA,38.6 >> test_data.csv
echo G,Jewell Loyd (67890),Jewell Loyd,67890,UTIL,9200,SEA@PHO,SEA,44.7 >> test_data.csv
echo F,Napheesa Collier (78901),Napheesa Collier,78901,UTIL,8800,MIN@CHI,MIN,41.2 >> test_data.csv
echo G,Kelsey Plum (89012),Kelsey Plum,89012,UTIL,8500,LVA@NYL,LVA,39.8 >> test_data.csv
echo G,Arike Ogunbowale (90123),Arike Ogunbowale,90123,UTIL,8300,DAL@ATL,DAL,38.4 >> test_data.csv
echo F,Jonquel Jones (01234),Jonquel Jones,01234,UTIL,8200,NYL@CON,NYL,37.9 >> test_data.csv

echo Running basic optimizer test...
python optimizer.py test_data.csv 1

echo.
echo Running advanced optimizer test with team stacking (LVA)...
python advanced_optimizer.py test_data.csv 1 LVA

echo.
echo Optimizer testing complete!
echo If you see lineups above, the optimizer is working correctly.

REM Clean up test data
del test_data.csv

pause
