@echo off
title Stopping Loco QC Server
cd /d "%~dp0"

echo ========================================================
echo               STOPPING LOCO QC SERVER
echo ========================================================

:: 1. Force kill via PowerShell (checks port 5000 and kills owning processes)
powershell.exe -NoProfile -Command "Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | ForEach-Object { Write-Host 'Killing PID on port 5000:' $_.OwningProcess; Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"

:: 2. Force kill any python process running from this venv directory
powershell.exe -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name like 'python%%'\" | Where-Object { $_.CommandLine -like '*Loco_QCChecklist_Python*' } | ForEach-Object { Write-Host 'Killing Python process:' $_.ProcessId; Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"

:: 3. Close any window titled Loco QC Waitress Server
taskkill /F /FI "WINDOWTITLE eq Loco QC Waitress Server*" /T >nul 2>&1

echo.
echo Server stop command executed. Checking port 5000...
powershell.exe -NoProfile -Command "$conn = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue; if ($conn) { Write-Host '[WARNING] Port 5000 still occupied by PID:' $conn.OwningProcess } else { Write-Host '[SUCCESS] Port 5000 is now FREE.' }"
echo ========================================================
