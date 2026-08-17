$projectRoot = Split-Path -Parent $PSScriptRoot
$startMonitor = Join-Path $PSScriptRoot "start-monitor.ps1"

& $startMonitor

$machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$env:Path = "$machinePath;$userPath"

$existingDashboard = Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -match [regex]::Escape($projectRoot) -and
    $_.CommandLine -match "streamlit"
}

if (-not $existingDashboard) {
    $uv = Get-Command uv -ErrorAction Stop
    Start-Process -FilePath $uv.Source -ArgumentList @("run", "streamlit", "run", "dashboard.py", "--server.headless", "true") -WorkingDirectory $projectRoot -WindowStyle Hidden
    Start-Sleep -Seconds 2
}

Start-Process "http://localhost:8501"
