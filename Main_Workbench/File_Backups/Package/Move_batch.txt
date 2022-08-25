@echo off
set thing=%date:~4,2%%date:~7,2%%date:~10,4%

cd C:\Users\zachary.t.thoroughgo\DES\Environment

move DESPurple%thing%.csv C:\Users\zachary.t.thoroughgo\DES\Environment\TenMinArchives

exit