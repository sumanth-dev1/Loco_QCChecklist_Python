@echo off
title Stopping Loco QC Server
cd /d "%~dp0"

echo ========================================================
echo               STOPPING LOCO QC SERVER
echo ========================================================

set found=0

:: Kill any process listening on port 5000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000" ^| findstr "LISTENING"') do (
    set found=1
    taskkill /F /PID %%a >nul 2>&1
)

:: Also close any window titled Loco QC Waitress Server
taskkill /F /FI "WINDOWTITLE eq Loco QC Waitress Server*" /T >nul 2>&1

timeout /t 1 >nul 2>&1

:: Verify port is freed
netstat -aon | findstr ":5000" | findstr "LISTENING" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [WARNING] Port 5000 is still in use. Retrying...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000" ^| findstr "LISTENING"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
)

echo.
echo Loco QC server has been stopped.
timeout /t 2 >nul
