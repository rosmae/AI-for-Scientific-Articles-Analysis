#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate || source venv/Scripts/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Build executable with PyInstaller
echo "Building executable with PyInstaller..."
pyinstaller ai_4_articles.spec

echo "Build complete! Executable is in the dist folder."

# Deactivate virtual environment
deactivate