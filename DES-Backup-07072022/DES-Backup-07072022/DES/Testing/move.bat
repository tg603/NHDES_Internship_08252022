@echo off
set time = echo %date:~4,2%%date:~7,2%%date:~10,4%

move Demo S:\ARD-Atmospheric\User\WorkingFiles\Thoroughgood

start python Demo.py

exit