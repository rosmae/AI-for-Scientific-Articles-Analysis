@echo off
REM filepath: c:\Users\raul\Documents\GitHub\AI-for-Scientific-Articles-Analysis\build.bat

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Build executable with PyInstaller
echo Building executable with PyInstaller...
pyinstaller ai_4_articles.spec

echo Build complete! Executable is in the dist folder.

REM Deactivate virtual environment
deactivate

REM Pause to see the output
pause