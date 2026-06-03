@echo off
setlocal
cd /d "%~dp0"

set "PORT=5173"
if not "%~1"=="" set "PORT=%~1"

where npm >nul 2>&1
if errorlevel 1 goto :no_npm

for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%PORT% .*LISTENING"') do (
  echo.
  echo Port %PORT% is already in use by PID %%P.
  echo Frontend may already be running at http://127.0.0.1:%PORT%
  echo If needed, run this script with another port, for example: start_frontend.bat 5501
  goto :eof
)

echo Starting SvelteKit dev server on http://0.0.0.0:%PORT%
npm run dev -- --host 0.0.0.0 --port %PORT% || goto :error
goto :eof

:no_npm
echo.
echo npm was not found.
echo Install Node.js LTS and ensure "npm" is in PATH.
pause
exit /b 1

:error
echo.
echo Failed to start frontend. Check the errors above.
pause
exit /b 1