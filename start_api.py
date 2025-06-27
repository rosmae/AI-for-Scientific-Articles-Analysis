#!/usr/bin/env python
"""
Startup script for Prime Time Medical Research Opportunities API
"""
import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    try:
        import uvicorn
        from main_api import app
        
        print("🚀 Starting Prime Time Medical Research Opportunities API...")
        print("📖 API Documentation will be available at: http://localhost:8000/docs")
        print("🔍 Health check: http://localhost:8000/health")
        print("⏹️  Press Ctrl+C to stop the server")
        print("-" * 60)
        
        uvicorn.run(
            "main_api:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you have installed all dependencies:")
        print("   pip install -r requirements_api.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting API: {e}")
        sys.exit(1) 