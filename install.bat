@echo off
echo Mouse Curve Analyzer - Installation Script
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH. Please install Python 3.6 or higher.
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python version: %PYTHON_VERSION%

REM Create virtual environment (optional)
echo.
set /p CREATE_VENV=Would you like to create a virtual environment? (recommended) [Y/n]: 

if /i not "%CREATE_VENV%"=="n" (
    echo Creating virtual environment...
    
    REM Check if venv module is available
    python -c "import venv" >nul 2>&1
    if %errorlevel% neq 0 (
        echo Error: The venv module is not available. Please install it or use pip directly.
        echo Continuing with system Python...
    ) else (
        python -m venv venv
        
        REM Activate virtual environment
        if exist "venv\Scripts\activate.bat" (
            call venv\Scripts\activate.bat
            echo Virtual environment created and activated.
            set PYTHON=venv\Scripts\python.exe
        ) else (
            echo Failed to create virtual environment. Continuing with system Python...
            set PYTHON=python
        )
    )
) else (
    set PYTHON=python
)

REM Install dependencies
echo.
echo Installing required packages...
%PYTHON% -m pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo Installation completed successfully!
    echo.
    echo To run the Mouse Curve Analyzer:
    if /i not "%CREATE_VENV%"=="n" if exist "venv\Scripts\activate.bat" (
        echo 1. Activate the virtual environment: venv\Scripts\activate.bat
        echo 2. Run the application: python mouse_curve.py
    ) else (
        echo Run the application: python mouse_curve.py
    )
    echo.
    echo For a simpler command-line version, you can also run:
    echo python example_basic_usage.py
) else (
    echo.
    echo Error: Failed to install required packages.
    exit /b 1
)

echo.
echo Press any key to exit...
pause >nul