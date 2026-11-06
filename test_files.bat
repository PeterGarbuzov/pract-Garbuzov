@echo off
cd /d "%~dp0"
py main.py --vfs vfs_files.json --script startup_files.txt
