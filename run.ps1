<#
  AI GTM OS — start / stop / status

    .\run.ps1            start both servers (detached — they survive closing this window)
    .\run.ps1 stop       stop them
    .\run.ps1 status     show whether they are up
    .\run.ps1 logs       tail the logs
    .\run.ps1 -Attached  run in this window instead (Ctrl+C to stop)

  Web  http://localhost:5173   login founder@demo.gtm / demo12345
  API  http://localhost:8000
#>
param(
    [ValidateSet('start', 'stop', 'restart', 'status', 'logs')]
    [string]$Action = 'start',
    [switch]$Attached
)

$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$Logs = Join-Path $Root '.logs'
$Py   = Join-Path $Root 'backend\.venv\Scripts\python.exe'

function Get-DevProcesses {
    Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='node.exe' OR Name='cmd.exe'" |
        Where-Object { $_.CommandLine -match 'manage\.py runserver|vite --port 5173' }
}

function Test-Endpoint($Url) {
    try { $null = Invoke-WebRequest -Uri $Url -TimeoutSec 3 -UseBasicParsing; $true } catch { $false }
}

function Show-Status {
    $api = Test-Endpoint 'http://localhost:8000/api/health/'
    $web = Test-Endpoint 'http://localhost:5173/'
    if ($api) {
        $h = (Invoke-WebRequest 'http://localhost:8000/api/health/' -UseBasicParsing).Content | ConvertFrom-Json
        Write-Host ("  API  UP    {0} - {1}" -f $h.ai_mode, $h.model) -ForegroundColor Green
    } else { Write-Host '  API  DOWN' -ForegroundColor Red }
    if ($web) { Write-Host '  WEB  UP    http://localhost:5173' -ForegroundColor Green }
    else      { Write-Host '  WEB  DOWN' -ForegroundColor Red }
    return ($api -and $web)
}

function Stop-Servers {
    $procs = Get-DevProcesses
    if (-not $procs) { Write-Host 'Nothing running.' -ForegroundColor DarkGray; return }
    foreach ($p in $procs) {
        Write-Host "  stopping PID $($p.ProcessId)" -ForegroundColor DarkGray
        Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 1
    Write-Host 'Stopped.' -ForegroundColor Yellow
}

function Start-Servers {
    if (-not (Test-Path $Py)) {
        Write-Host "No virtualenv at $Py" -ForegroundColor Red
        Write-Host 'Run:  cd backend; python -m venv .venv; .venv\Scripts\pip install -r requirements.txt'
        exit 1
    }
    if (-not (Test-Path (Join-Path $Root 'frontend\node_modules'))) {
        Write-Host 'Installing frontend dependencies...' -ForegroundColor Cyan
        Push-Location (Join-Path $Root 'frontend'); npm install; Pop-Location
    }

    Stop-Servers
    New-Item -ItemType Directory -Force -Path $Logs | Out-Null

    Push-Location (Join-Path $Root 'backend')
    & $Py manage.py migrate --no-input | Out-Null
    Pop-Location

    if ($Attached) {
        Write-Host 'Starting in this window. Ctrl+C to stop.' -ForegroundColor Cyan
        Start-Process -FilePath $env:ComSpec -ArgumentList '/c', 'npx vite --port 5173' `
            -WorkingDirectory (Join-Path $Root 'frontend') -WindowStyle Minimized | Out-Null
        Push-Location (Join-Path $Root 'backend')
        & $Py manage.py runserver 8000
        Pop-Location
        return
    }

    # Detached: not children of this shell, so they outlive the window.
    $api = Start-Process -FilePath $Py -ArgumentList 'manage.py', 'runserver', '8000', '--noreload' `
        -WorkingDirectory (Join-Path $Root 'backend') -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput "$Logs\api.log" -RedirectStandardError "$Logs\api.err"
    $web = Start-Process -FilePath $env:ComSpec -ArgumentList '/c', 'npx vite --port 5173' `
        -WorkingDirectory (Join-Path $Root 'frontend') -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput "$Logs\web.log" -RedirectStandardError "$Logs\web.err"

    $api.Id | Set-Content "$Logs\api.pid"
    $web.Id | Set-Content "$Logs\web.pid"
    Write-Host "  api PID $($api.Id)  |  web PID $($web.Id)" -ForegroundColor DarkGray

    Write-Host 'Waiting for servers...' -ForegroundColor Cyan
    foreach ($i in 1..25) {
        Start-Sleep -Seconds 2
        if ((Test-Endpoint 'http://localhost:8000/api/health/') -and (Test-Endpoint 'http://localhost:5173/')) { break }
    }

    Write-Host ''
    if (Show-Status) {
        Write-Host ''
        Write-Host '  Open  http://localhost:5173' -ForegroundColor White
        Write-Host '  Login founder@demo.gtm / demo12345' -ForegroundColor DarkGray
        Write-Host '  Stop  .\run.ps1 stop' -ForegroundColor DarkGray
    } else {
        Write-Host ''
        Write-Host "  Something did not come up. Check $Logs\api.err and $Logs\web.err" -ForegroundColor Yellow
    }
}

switch ($Action) {
    'start'   { Start-Servers }
    'stop'    { Stop-Servers }
    'restart' { Start-Servers }
    'status'  { Show-Status | Out-Null }
    'logs'    { Get-Content "$Logs\api.log", "$Logs\web.log" -Tail 25 -Wait }
}
