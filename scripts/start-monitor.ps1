$projectRoot = Split-Path -Parent $PSScriptRoot
$machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$env:Path = "$machinePath;$userPath"

$existingMonitor = Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -match [regex]::Escape($projectRoot) -and
    $_.CommandLine -match "medidor-consumo"
}

if ($existingMonitor) {
    Write-Output "O monitor ja esta em execucao."
    exit 0
}

$uv = Get-Command uv -ErrorAction Stop
Start-Process -FilePath $uv.Source -ArgumentList @("run", "medidor-consumo") -WorkingDirectory $projectRoot -WindowStyle Hidden

Write-Output "Monitor iniciado em segundo plano."
