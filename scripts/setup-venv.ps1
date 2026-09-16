# Create .venv, install requirements-dev.txt, download Chromium for Playwright.
# Run from anywhere; the repo root is inferred from this script's location.
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $RepoRoot

function Resolve-Python {
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) { return $py.Source }
    throw "Python 3.12+ not found on PATH. Install Python and retry."
}

$systemPython = Resolve-Python
$venvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "Creating .venv ..."
    if ((Split-Path $systemPython -Leaf) -eq "py.exe") {
        & $systemPython -3 -m venv .venv
    } else {
        & $systemPython -m venv .venv
    }
}

Write-Host "Installing requirements-dev.txt ..."
& $venvPython -m pip install -U pip
& $venvPython -m pip install -r (Join-Path $RepoRoot "requirements-dev.txt")

Write-Host "Installing Playwright Chromium ..."
& $venvPython -m playwright install chromium

Write-Host @"

Venv ready at .venv

Activate (PowerShell):
  .\.venv\Scripts\Activate.ps1

If Activate.ps1 is blocked:
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

Compose must be up (web healthy on http://localhost:8080) before UI tests.

API tests:
  python -m pytest tests/api -v

UI tests:
  python -m pytest -c tests/ui/pytest.ini tests/ui -v

CLI tests:
  python -m pytest python/tests -q

Without activating, prefix the same commands with .\.venv\Scripts\python.exe -m
"@
