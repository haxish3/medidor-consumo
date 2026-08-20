$projectRoot = Split-Path -Parent $PSScriptRoot
$machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$env:Path = "$machinePath;$userPath"

$existingMonitor = Get-Process -Name "medidor-consumo" -ErrorAction SilentlyContinue

if ($existingMonitor) {
    Write-Output "O monitor ja esta em execucao."
    exit 0
}

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
$isAdministrator = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdministrator) {
    Start-ScheduledTask -TaskName "Medidor de Consumo"
    Write-Output "Solicitada a inicializacao elevada do monitor."
    exit 0
}

$uv = Get-Command uv -ErrorAction Stop
Start-Process -FilePath $uv.Source -ArgumentList @("run", "medidor-consumo") -WorkingDirectory $projectRoot -WindowStyle Hidden

Write-Output "Monitor iniciado em segundo plano."
