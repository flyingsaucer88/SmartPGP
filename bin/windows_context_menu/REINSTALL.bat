@echo off
REM AEPGP Context Menu - Reinstall Script
REM This script uninstalls old menu entries and installs the new cascading menu

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This script requires Administrator privileges.
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo ======================================================================
echo AEPGP Context Menu - Reinstall (Uninstall + Install)
echo ======================================================================
echo.
echo This script will:
echo   1. Remove old AEPGP context menu entries
echo   2. Install new cascading menu structure
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

REM Get the directory where this script is located
cd /d "%~dp0"

REM Find Python executable
set PYTHON_CMD=python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    set PYTHON_CMD=py
    where py >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Python not found in PATH
        echo Please install Python or add it to your PATH
        pause
        exit /b 1
    )
)

echo.
echo Step 1: Uninstalling old menu entries...
echo ======================================================================
%PYTHON_CMD% uninstall_menu.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Uninstall failed with error code %ERRORLEVEL%
    echo Please check the error messages above.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo.
echo Step 2: Installing new cascading menu...
echo ======================================================================
%PYTHON_CMD% install_menu.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Install failed with error code %ERRORLEVEL%
    echo Please check the error messages above.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ======================================================================
echo Reinstallation completed successfully!
echo ======================================================================
echo.
echo You should now see the new AEPGP cascading menu when you:
echo   - Right-click any file
echo   - Right-click on Desktop background
echo.
pause
