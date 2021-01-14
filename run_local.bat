@echo off

if not "%1"=="" (set /A n=%1 ) else ( set /A n=1 )

start "server" test.py

FOR /L %%A IN (1,1,%n%) DO (
  start "client #%%A" client.py %2
)