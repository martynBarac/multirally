@echo off

if not "%1"=="" (set /A n=%1 ) else ( set /A n=1 )
REM set /A n = 1
ECHO %n%

start "" test.py
FOR /L %%A IN (1,1,%n%) DO (
  start "" client.py
)