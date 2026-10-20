# Local offline demonstration of fictional companies; no Harvey agent, SMTP, or LinkedIn.
# From repository root: powershell -ExecutionPolicy Bypass -File pilots/etatloc/run-demo.ps1
$ErrorActionPreference = "Stop"
$Pilot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = (Resolve-Path (Join-Path $Pilot "../..")).Path
$Venv = Join-Path $Pilot ".venv"
$Python = Join-Path $Venv "Scripts/python.exe"
if (-not (Test-Path $Python)) {
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if (-not $launcher) { throw "Python launcher 'py' not found; install Python 3.11 or 3.12." }
    & py -3.12 -m venv $Venv
    if ($LASTEXITCODE -ne 0) { throw "Python 3.12 unavailable: use a supported Python and create pilots/etatloc/.venv manually." }
}
& $Python -m pip install "PyYAML>=6.0.1,<7"
if ($LASTEXITCODE -ne 0) { throw "Cannot install YAML dependency." }
& $Python (Join-Path $Pilot "preflight.py")
if ($LASTEXITCODE -ne 0) { throw "Unsafe demo settings. STOP." }
& $Python (Join-Path $Pilot "qualify_demo.py")
if ($LASTEXITCODE -ne 0) { throw "Demo qualification failed. STOP." }
Write-Host "CSV: $Pilot/qualification_demo.csv"
Write-Host "No Harvey agent was launched, no messages were sent."
