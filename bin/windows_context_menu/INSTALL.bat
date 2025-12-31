@echo off
REM AEPGP Windows Context Menu - Easy Installer
REM This batch file installs dependencies and the context menu integration

echo ========================================
echo AEPGP Context Menu - Easy Installer
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
        echo Please install Python from https://www.python.org/downloads/
        echo Make sure to check "Add Python to PATH" during installation
        echo.
        pause
        exit /b 1
    )
)

echo [1/3] Python found:
%PYTHON_CMD% --version
echo.

REM Install Python dependencies
echo [2/3] Installing Python dependencies...
%PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo WARNING: Failed to install some dependencies
    echo You may need to run: pip install pyscard cryptography
    echo.
)
echo.

REM Run the installer (will request elevation)
echo [3/3] Installing context menu...
echo.
echo NOTE: You will be prompted for Administrator privileges
echo.
%PYTHON_CMD% install_menu.py

echo.
echo ========================================
echo Installation process completed
echo ========================================
echo.
pause
