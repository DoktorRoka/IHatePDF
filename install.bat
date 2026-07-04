@echo off
echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
echo   IHatePDF Auto-Installer for Windows
echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
echo.

:: python check
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed
    echo Install python from pythong.org and make sure to check "Add to PATH".
    pause
    exit /b
)

:: create venv
echo creating venv...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Can't create venv.
    pause
    exit /b
)

:: activate venv and install libs
echo activating venv and updating pip...
call venv\Scripts\activate
python -m pip install --upgrade pip

echo installing requirements.txt...
pip install -r requirements.txt

echo.
echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
echo   installation done
echo   for launch use: venv\Scripts\python.exe ihatepdf.py
echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
pause