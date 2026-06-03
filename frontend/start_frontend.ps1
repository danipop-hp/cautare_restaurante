# Start a simple static file server to serve the frontend.
param(
    [int]$port = 5173
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $scriptDir

try {
    $npm = Get-Command npm -ErrorAction SilentlyContinue
    if (-not $npm) {
        Write-Error "npm was not found. Install Node.js LTS and ensure npm is in PATH."
        exit 1
    }

    Write-Output "Starting SvelteKit dev server on http://0.0.0.0:$port"
    & npm run dev -- --host 0.0.0.0 --port $port
}
finally {
    Pop-Location
}
