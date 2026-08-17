@echo off
title Build ShotgunKeys Standalone EXE
color 0A

echo =======================================================
echo        SHOTGUNKEYS - WINDOWS EXE BUILD SCRIPT
echo =======================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python is not installed or not in system PATH!
    echo Please install Python 3.9+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [1/3] Checking and installing build requirements...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Failed to install dependencies from requirements.txt!
    pause
    exit /b 1
)

echo.
echo [2/3] Generating icons if missing...
python make_icon.py

echo.
echo [3/3] Packaging ShotgunKeys with PyInstaller...
python build_exe.py

if %errorlevel% equ 0 (
    echo.
    echo =======================================================
    echo    SUCCESS! Executable is ready at: dist\ShotgunKeys.exe
    echo =======================================================
) else (
    color 0C
    echo.
    echo [ERROR] PyInstaller build failed. Check the errors above.
)

echo.
pause
