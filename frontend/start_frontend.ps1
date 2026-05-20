# Start a simple static file server to serve the frontend.
param(
    [int]$port = 5500,
    [string]$pythonCmd = "py"
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $scriptDir

try {
    $venvPython = Join-Path "..\.venv" "Scripts\python.exe"
    Write-Output "Starting static server on http://127.0.0.1:$port"

    if (Test-Path $venvPython) {
        & $venvPython -m http.server $port
    } elseif ($pythonCmd -eq "py") {
        & py -3 -m http.server $port
    } else {
        & $pythonCmd -m http.server $port
    }
}
finally {
    Pop-Location
}
