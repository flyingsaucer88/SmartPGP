@echo off
REM AEPGP Windows Context Menu - Easy Uninstaller

echo ========================================
echo AEPGP Context Menu - Uninstaller
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    pause
    exit /b 1
)

REM Run the uninstaller (will request elevation)
echo Launching uninstaller...
echo.
echo NOTE: You will be prompted for Administrator privileges
echo.
python uninstall_menu.py

echo.
pause
