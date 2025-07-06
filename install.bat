@echo off
echo.
echo 🎓 MESHACHVETZ INSTALLATION - Windows
echo =========================================
echo.
echo This will install Meshachvetz on your computer.
echo Please wait while we set everything up...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Run the installation script
echo 📦 Running installation script...
python install.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Installation failed. Please check the errors above.
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Installation complete!
echo.
echo You can now use Meshachvetz by:
echo   1. Double-clicking "run_meshachvetz.bat"
echo   2. Or opening Command Prompt in this folder and typing:
echo      run_meshachvetz.bat score your_students.csv
echo.
pause 