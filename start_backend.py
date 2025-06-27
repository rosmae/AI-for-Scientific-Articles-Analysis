#!/usr/bin/env python
"""
Startup script for Prime Time Medical Research Opportunities API Backend
"""
import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

if __name__ == "__main__":
    try:
        import uvicorn
        
        print("🚀 Starting Prime Time Medical Research Opportunities API Backend...")
        print("📖 API Documentation will be available at: http://localhost:8000/docs")
        print("🔍 Health check: http://localhost:8000/health")
        print("⏹️  Press Ctrl+C to stop the server")
        print("-" * 60)
        
        # Run uvicorn directly with the module path to main.py in the backend directory
        uvicorn.run(
            "backend.main:app",  # Change this to correct module path
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you have installed all dependencies:")
        print("   Run: .venv/Scripts/pip install -r requirements_api.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting API: {e}")
        sys.exit(1)
