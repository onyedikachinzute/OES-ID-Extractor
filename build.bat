@echo off
echo ===================================================
echo               STARTING PYINSTALLER BUILD           
echo ===================================================

:: 1. Clean up old build and dist folders to avoid conflicts
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

:: 2. Check if .venv exists; if not, create it
if not exist .venv (
    echo .venv folder not found. Initializing virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b
    )
)

:: 3. Activate the Virtual Environment (.venv)
echo Activating Virtual Environment...
call .venv\Scripts\activate.bat

:: 4. Update Pip and Install Requirements
if exist requirements.txt (
    echo Updating pip...
    python -m pip install --upgrade pip
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
) else (
    echo WARNING: requirements.txt not found. Skipping dependency installation.
)

:: 5. Purge obsolete pathlib package if it was pulled in
echo Cleaning environment conflicts...
pip uninstall -y pathlib

:: 6. Ensure PyInstaller is installed inside the .venv
echo Verifying PyInstaller installation...
pip install pyinstaller

:: 7. Run PyInstaller with your custom flags
echo Running PyInstaller...
pyinstaller --onefile --noconsole --name="OES-ID-Extractor" --icon="icon.ico" --add-data "assets/;assets/" main.py

echo ===================================================
echo               BUILD COMPLETE! CLEANING UP          
echo ===================================================

:: 8. Deactivate the virtual environment
call deactivate

:: 9. Clean up temporary files left behind by PyInstaller
if exist OES-ID-Extractor.spec del /f OES-ID-Extractor.spec
if exist build rmdir /s /q build

echo.
echo Launching your file location...

:: 10. Auto-open the dist folder in Windows Explorer
if exist dist start "" "dist"

pause
