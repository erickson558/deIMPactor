Set-Location $PSScriptRoot

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "No se encontró la .venv del proyecto en $python"
}

& $python -m pip install -r requirements.txt
& $python -m PyInstaller .\deIMPactor.spec --noconfirm
