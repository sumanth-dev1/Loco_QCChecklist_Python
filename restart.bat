@echo off
setlocal enabledelayedexpansion
title Restarting Loco QC Server
cd /d "%~dp0"

echo ========================================================
echo               RESTARTING LOCO QC SERVER
echo ========================================================

:: 1. Stop existing process on port 5000
echo Stopping any running server...
powershell.exe -NoProfile -Command "Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
powershell.exe -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name like 'python%%'\" | Where-Object { $_.CommandLine -like '*Loco_QCChecklist_Python*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
taskkill /F /FI "WINDOWTITLE eq Loco QC Waitress Server*" /T >nul 2>&1

:: 2. Clean pycache
echo Cleaning Python cache...
if exist "routes\__pycache__" (
    del /q /f "routes\__pycache__\part_details*.pyc" >nul 2>&1
)

:: 3. Wait for port to free
ping 127.0.0.1 -n 2 >nul

:: 4. Start fresh server
echo.
echo Starting fresh Loco QC Waitress Server...
start "Loco QC Waitress Server" cmd /c ""%~dp0venv\Scripts\python.exe" run.py || pause"

:: 5. Wait for readiness
echo Waiting for server to initialize on http://localhost:5000/ ...
set /a attempts=0

:WAIT_LOOP
set /a attempts+=1
ping 127.0.0.1 -n 2 >nul

curl.exe -s -m 2 http://localhost:5000/health >nul 2>&1
if !ERRORLEVEL! equ 0 (
    echo.
    echo ========================================================
    echo Server is ready! (Connected in !attempts! seconds)
    echo Opening application at: http://localhost:5000/
    echo ========================================================
    start http://localhost:5000/
    exit /b 0
)

if !attempts! geq 15 (
    echo.
    echo [ERROR] Server took too long to start. Please check the 'Loco QC Waitress Server' terminal window for errors.
    pause
    exit /b 1
)

goto WAIT_LOOP

