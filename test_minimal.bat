@echo off
cd /d "%~dp0"
py main.py --vfs vfs_minimal.json --script startup.txt
