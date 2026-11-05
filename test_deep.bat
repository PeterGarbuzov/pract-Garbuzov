@echo off
cd /d "%~dp0"
py main.py --vfs vfs_deep.json --script startup.txt
