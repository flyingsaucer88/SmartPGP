@echo off
REM AEPGP Context Menu - Build Executable Script
REM This script builds a standalone .exe file using PyInstaller

echo ========================================
echo AEPGP Context Menu - Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [1/5] Checking Python installation...
python --version
echo.

REM Check if PyInstaller is installed
echo [2/5] Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
) else (
    echo PyInstaller is already installed
)
echo.

REM Check if pyscard is installed
echo [3/5] Checking pyscard...
pip show pyscard >nul 2>&1
if errorlevel 1 (
    echo pyscard not found. Installing...
    pip install pyscard
    if errorlevel 1 (
        echo ERROR: Failed to install pyscard
        pause
        exit /b 1
    )
) else (
    echo pyscard is already installed
)
echo.

REM Clean previous build
echo [4/5] Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
if exist handlers\__pycache__ rmdir /s /q handlers\__pycache__
echo.

REM Build executable
echo [5/5] Building executable...
echo This may take a few minutes...
echo.
pyinstaller --clean aepgp_installer.spec

if errorlevel 1 (
    echo.
    echo ========================================
    echo BUILD FAILED
    echo ========================================
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD SUCCESSFUL!
echo ========================================
echo.
echo The executable has been created:
echo   dist\AEPGP_Installer.exe
echo.
echo File size:
dir dist\AEPGP_Installer.exe | find "AEPGP_Installer.exe"
echo.
echo You can now distribute this single .exe file to users.
echo Users do NOT need Python installed to run it.
echo.
pause
