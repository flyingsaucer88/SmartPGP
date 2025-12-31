@echo off
REM AEPGP Windows Context Menu - Easy Uninstaller

echo ========================================
echo AEPGP Context Menu - Uninstaller
echo ========================================
echo.

REM Get the directory where this script is located
cd /d "%~dp0"

REM Find Python executable
set PYTHON_CMD=python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    set PYTHON_CMD=py
    where py >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Python is not installed or not in PATH
        echo.
        pause
        exit /b 1
    )
)

REM Run the uninstaller (will request elevation)
echo Launching uninstaller...
echo.
echo NOTE: You will be prompted for Administrator privileges
echo.
%PYTHON_CMD% uninstall_menu.py

echo.
pause
