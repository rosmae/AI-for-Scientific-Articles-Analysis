#!/usr/bin/env python
"""
Setup script for the backend environment
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command):
    """Run a command and print output"""
    print(f"Running: {command}")
    process = subprocess.run(command, shell=True, capture_output=True, text=True)
    if process.returncode != 0:
        print(f"❌ Error: {process.stderr}")
        return False
    print(f"✅ Success!")
    return True

def main():
    print("🔧 Setting up backend environment...")
    
    # Get the path to the Python executable in the virtual environment
    venv_path = Path(__file__).parent / ".venv"
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip"
    else:
        pip_path = venv_path / "bin" / "pip"
    
    # Install required packages
    print("\n📦 Installing required packages...")
    packages = [
        "fastapi", 
        "uvicorn[standard]", 
        "pydantic", 
        "pydantic-settings", 
        "python-dotenv", 
        "transformers", 
        "torch", 
        "keybert", 
        "matplotlib",
        "scikit-learn",
        "numpy",
        "requests"
    ]
    
    if not run_command(f"{pip_path} install {' '.join(packages)}"):
        return
    
    print("\n🚀 Setup complete! You can now run the backend with:")
    print("python start_backend.py")

if __name__ == "__main__":
    main()
