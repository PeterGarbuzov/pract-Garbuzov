@echo off
cd /d "%~dp0"
py main.py --vfs vfs_invalid.json
py main.py --vfs missing.json
