@echo off
setlocal
cd /d "%~dp0\.."

if not exist ".venv\Scripts\python.exe" (
  set "BOOTSTRAP_PY="
  py -3 --version >nul 2>&1
  if not errorlevel 1 (
    set "BOOTSTRAP_PY=py -3"
  ) else (
    python --version >nul 2>&1
    if not errorlevel 1 (
      set "BOOTSTRAP_PY=python"
    )
  )

  if "%BOOTSTRAP_PY%"=="" goto :no_python

  echo Creating virtual environment...
  %BOOTSTRAP_PY% -m venv .venv || goto :error
)

set "PYTHON_CMD=.venv\Scripts\python.exe"

for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":8000 .*LISTENING"') do (
  echo.
  echo Port 8000 is already in use by PID %%P.
  echo Backend might already be running at http://127.0.0.1:8000
  echo Stop the existing process or use another port.
  goto :eof
)

echo Installing dependencies...
%PYTHON_CMD% -m pip install -r requirements.txt || goto :error

echo Starting FastAPI on http://127.0.0.1:8000
%PYTHON_CMD% -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
goto :eof

:no_python
echo.
echo Python interpreter was not found.
echo Install Python 3.10+ and ensure either "py" or "python" is in PATH.
pause
exit /b 1

:error
echo.
echo Failed to start backend. Check the errors above.
pause
exit /b 1