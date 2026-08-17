@echo off
title ShotgunKeys - Tactical Sound Engine
color 06

echo =======================================================
echo           💥 STARTING SHOTGUNKEYS FOR WINDOWS 💥
echo =======================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python is not found in PATH!
    echo Please install Python 3.9+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Check if requirements are installed
python -c "import pygame, pystray, PIL, pynput" >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing required libraries...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        color 0C
        echo [ERROR] Dependency installation failed!
        pause
        exit /b 1
    )
)

:: Run ShotgunKeys
echo Starting ShotgunKeys...
start "" pythonw main.py

exit /b 0
