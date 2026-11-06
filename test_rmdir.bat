@echo off
cd /d "%~dp0"
py main.py --vfs vfs_rmdir.json --script startup_rmdir.txt
pause
