Add-Type -AssemblyName System.Drawing

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$desktopDir = [System.Environment]::GetFolderPath('Desktop')
$iconPath = Join-Path $projectDir "static\favicon.ico"
$logoPath = Join-Path $projectDir "static\hbl_logo.jpg"

# Generate favicon.ico if not exists
if (-not (Test-Path $iconPath) -and (Test-Path $logoPath)) {
    try {
        $bmp = [System.Drawing.Bitmap]::FromFile($logoPath)
        $thumb = New-Object System.Drawing.Bitmap($bmp, 64, 64)
        $iconHandle = $thumb.GetHicon()
        $icon = [System.Drawing.Icon]::FromHandle($iconHandle)
        $stream = [System.IO.File]::OpenWrite($iconPath)
        $icon.Save($stream)
        $stream.Close()
        $bmp.Dispose()
        $thumb.Dispose()
        Write-Output "Created favicon.ico"
    } catch {
        Write-Warning "Could not generate icon: $_"
    }
}

# 1. Create Desktop Shortcut: Loco QC
$wsh = New-Object -ComObject WScript.Shell
$shortcutPath = Join-Path $desktopDir "Loco QC.lnk"
$shortcut = $wsh.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "wscript.exe"
$shortcut.Arguments = "`"$projectDir\launch_silent.vbs`""
$shortcut.WorkingDirectory = $projectDir
$shortcut.Description = "Launch Loco QC Application (http://localhost:5000/)"
if (Test-Path $iconPath) {
    $shortcut.IconLocation = "$iconPath,0"
} else {
    $shortcut.IconLocation = "shell32.dll,13"
}
$shortcut.Save()
Write-Output "Created Desktop Shortcut at: $shortcutPath"

# 2. Also create a URL shortcut on Desktop as backup
$urlPath = Join-Path $desktopDir "Loco QC (Web Link).url"
$urlContent = @"
[InternetShortcut]
URL=http://localhost:5000/
IconIndex=0
IconFile=$iconPath
"@
[System.IO.File]::WriteAllText($urlPath, $urlContent)
Write-Output "Created Web Link at: $urlPath"

# 3. Add to Windows Startup folder so server runs automatically on boot
$startupDir = [System.Environment]::GetFolderPath('Startup')
$startupShortcutPath = Join-Path $startupDir "Loco QC Server.lnk"
$startupShortcut = $wsh.CreateShortcut($startupShortcutPath)
$startupShortcut.TargetPath = "wscript.exe"
$startupShortcut.Arguments = "`"$projectDir\start_server_background.vbs`""
$startupShortcut.WorkingDirectory = $projectDir
$startupShortcut.Description = "Auto-start Loco QC Waitress Server in background on Windows login"
if (Test-Path $iconPath) {
    $startupShortcut.IconLocation = "$iconPath,0"
}
$startupShortcut.Save()
Write-Output "Created Startup Shortcut at: $startupShortcutPath"
