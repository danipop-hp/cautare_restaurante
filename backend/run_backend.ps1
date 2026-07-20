# Create a virtual environment, install dependencies and run the FastAPI app.
# Uses the venv Python directly to avoid PowerShell activation issues.
param(
    [string]$venvName = ".venv",
    [string]$pythonCmd = "py"
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Resolve-Path (Join-Path $scriptDir "..")
Push-Location $projectRoot

try {
    if (-not (Test-Path $venvName)) {
        Write-Output "Creating virtual environment '$venvName'..."
        if ($pythonCmd -eq "py") {
            & py -3 -m venv $venvName
        } else {
            & $pythonCmd -m venv $venvName
        }
    }

    $venvPython = Join-Path $venvName "Scripts\python.exe"
    if (-not (Test-Path $venvPython)) {
        throw "Virtual environment python not found: $venvPython"
    }

    Write-Output "Installing dependencies..."
    & $venvPython -m pip install -r requirements.txt

    Write-Output "Starting uvicorn (FastAPI) on http://0.0.0.0:8000"
    & $venvPython -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
}
finally {
    Pop-Location
}