@echo off
title TDU2 Save File Toolkit WebGUI
cd /d "%~dp0"
echo ============================================================
echo   TDU2 Save File Toolkit - Starting WebGUI Server
echo ============================================================
echo.
python tdu2_webgui.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Python failed to start tdu2_webgui.py.
    echo Please make sure Python 3.8+ is installed and in your system PATH.
    pause
)
