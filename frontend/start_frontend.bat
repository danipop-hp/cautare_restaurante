@echo off
setlocal
cd /d "%~dp0"

set "PORT=5500"
if not "%~1"=="" set "PORT=%~1"

set "PYTHON_CMD="
if exist "..\.venv\Scripts\python.exe" (
  set "PYTHON_CMD=..\.venv\Scripts\python.exe"
) else (
  py -3 --version >nul 2>&1
  if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
  ) else (
    python --version >nul 2>&1
    if not errorlevel 1 (
      set "PYTHON_CMD=python"
    )
  )
)

if "%PYTHON_CMD%"=="" goto :no_python

for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%PORT% .*LISTENING"') do (
  echo.
  echo Port %PORT% is already in use by PID %%P.
  echo Frontend may already be running at http://127.0.0.1:%PORT%
  echo If needed, run this script with another port, for example: start_frontend.bat 5501
  goto :eof
)

echo Starting static server on http://127.0.0.1:%PORT%
%PYTHON_CMD% -m http.server %PORT% || goto :error
goto :eof

:no_python
echo.
echo Python interpreter was not found.
echo Install Python 3.10+ and ensure either "py" or "python" is in PATH.
pause
exit /b 1

:error
echo.
echo Failed to start frontend. Check the errors above.
pause
exit /b 1