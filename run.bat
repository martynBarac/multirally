set /p ADDR="ip:port > "
echo %ADDR%
python client_test.py %ADDR%
pause