@echo off
REM Force refresh Windows Explorer to update context menus

echo Restarting Windows Explorer to refresh context menus...
echo.

taskkill /F /IM explorer.exe
timeout /t 2 /nobreak >nul
start explorer.exe

echo.
echo Windows Explorer restarted successfully!
echo.
echo Please try right-clicking a file again to see the updated AEPGP menu.
echo.
pause
