set /p ADDR="ip:port > "
echo %ADDR%
python client.py %ADDR%
pause