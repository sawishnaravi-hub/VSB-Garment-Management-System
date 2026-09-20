@echo off
title VSB Garment Manufacturing Company Management System
echo ====================================================================
echo      VSB GARMENT MANUFACTURING COMPANY MANAGEMENT SYSTEM
echo ====================================================================
echo.

cd /d "%~dp0"

:: 1. Detect Python command
set "PYTHON_CMD="

py -0 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=py"
    goto :run_app
)

if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
    goto :run_app
)

python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=python"
    goto :run_app
)

echo [ERROR] Python was not found on your system.
echo Please install Python 3 or make sure Python is on your PATH.
pause
exit /b 1

:run_app
echo [OK] Using Python runner: %PYTHON_CMD%
echo [OK] Initializing application on http://localhost:5000 ...
echo [OK] Automatically opening your default web browser...
echo.

:: Automatically open browser after 2 seconds
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:5000"

:: Start application
"%PYTHON_CMD%" app.py

pause
