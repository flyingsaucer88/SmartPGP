@echo off
REM AEPGP Windows Context Menu - Easy Installer
REM This batch file installs dependencies and the context menu integration

echo ========================================
echo AEPGP Context Menu - Easy Installer
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [1/3] Python found:
python --version
echo.

REM Install Python dependencies
echo [2/3] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo WARNING: Failed to install some dependencies
    echo You may need to run: pip install pyscard
    echo.
)
echo.

REM Run the installer (will request elevation)
echo [3/3] Installing context menu...
echo.
echo NOTE: You will be prompted for Administrator privileges
echo.
python install_menu.py

echo.
echo ========================================
echo Installation process completed
echo ========================================
echo.
pause
