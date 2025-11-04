@echo off
REM Pylint Tests - Windows Batch Launcher
REM Quick launcher for pylint analysis on Windows

echo 🚀 Pylint Tests for Test Case API Project
echo ================================================

REM Change to the pylint_tests directory
cd /d "%~dp0"

echo Current directory: %cd%
echo.

:menu
echo 📋 Choose an option:
echo   [1] Quick Test (Fast analysis)
echo   [2] Full Analysis (Complete HTML report)
echo   [3] View Latest Report
echo   [4] List All Reports
echo   [5] Setup/Install Dependencies
echo   [Q] Quit
echo.

set /p choice="Enter your choice (1-5, Q): "

if /i "%choice%"=="1" (
    echo.
    echo 🔍 Running Quick Test...
    python quick_test.py
    echo.
    pause
    goto menu
)

if /i "%choice%"=="2" (
    echo.
    echo 📊 Running Full Analysis...
    python run_pylint_tests.py
    echo.
    echo ✅ Analysis complete! Report generated.
    pause
    goto menu
)

if /i "%choice%"=="3" (
    echo.
    echo 🌐 Opening Latest Report...
    python launcher.py
    echo.
    pause
    goto menu
)

if /i "%choice%"=="4" (
    echo.
    python launcher.py list
    echo.
    pause
    goto menu
)

if /i "%choice%"=="5" (
    echo.
    echo 🔧 Running Setup...
    python setup.py
    echo.
    pause
    goto menu
)

if /i "%choice%"=="q" (
    echo.
    echo 👋 Goodbye!
    exit /b 0
)

echo ❌ Invalid choice. Please try again.
echo.
goto menu