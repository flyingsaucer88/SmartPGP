@echo off
REM AEPGP Context Menu - MSI Installer Build Script
REM Creates a Windows MSI installer package

echo ========================================
echo AEPGP Context Menu - MSI Builder
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

echo [1/4] Checking Python installation...
python --version
echo.

REM Install cx_Freeze if needed
echo [2/4] Checking cx_Freeze...
pip show cx_Freeze >nul 2>&1
if errorlevel 1 (
    echo cx_Freeze not found. Installing...
    pip install cx_Freeze
    if errorlevel 1 (
        echo ERROR: Failed to install cx_Freeze
        pause
        exit /b 1
    )
) else (
    echo cx_Freeze is already installed
)
echo.

REM Install pyscard if needed
echo [3/4] Checking pyscard...
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
echo Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo.

REM Build MSI
echo [4/4] Building MSI installer...
echo This may take a few minutes...
echo.
python create_msi.py bdist_msi

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
echo The MSI installer has been created in the dist\ folder
echo.
dir dist\*.msi
echo.
echo You can now distribute this .msi file to users.
echo Users can install it like any other Windows software.
echo.
pause
