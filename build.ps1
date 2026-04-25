Set-Location $PSScriptRoot

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "No se encontró la .venv del proyecto en $python"
}

& $python -m pip install -r requirements.txt
& $python -m PyInstaller .\deIMPactor.spec --noconfirm

$distExe = Join-Path $PSScriptRoot "dist\deIMPactor.exe"
$rootExe = Join-Path $PSScriptRoot "deIMPactor.exe"
if (Test-Path $distExe) {
    Copy-Item $distExe $rootExe -Force
    Write-Host "Ejecutable actualizado en: $rootExe"
} else {
    throw "No se encontro el ejecutable esperado en $distExe"
}
