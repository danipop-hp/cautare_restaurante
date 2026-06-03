@echo off
setlocal
cd /d "%~dp0"

call :kill_port 8000 "Backend"
call :kill_port 5173 "Frontend"

echo Starting backend and frontend in separate windows...
start "Urban Plate Backend" cmd /k "backend\run_backend.bat"
start "Urban Plate Frontend" cmd /k "frontend\start_frontend.bat"

echo.
echo Open in browser: http://127.0.0.1:5173
goto :eof

:kill_port
set "TARGET_PORT=%~1"
set "SERVICE_NAME=%~2"
set "FOUND_PID="

for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%TARGET_PORT% .*LISTENING"') do (
	set "FOUND_PID=%%P"
	echo [%SERVICE_NAME%] Port %TARGET_PORT% is busy ^(PID %%P^). Stopping old process...
	taskkill /PID %%P /F >nul 2>&1
	if errorlevel 1 (
		echo [%SERVICE_NAME%] Could not stop PID %%P. Close it manually if startup fails.
	) else (
		echo [%SERVICE_NAME%] Old process stopped.
	)
)

if not defined FOUND_PID (
	echo [%SERVICE_NAME%] Port %TARGET_PORT% is free.
)

exit /b 0