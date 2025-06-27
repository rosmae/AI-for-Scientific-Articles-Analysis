#!/usr/bin/env python
"""
Direct runner for the backend FastAPI application
"""
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    # Run directly using the Python module
    os.chdir(backend_dir)
    
    try:
        # Import and run the FastAPI app directly
        from main import app
        import uvicorn
        
        print("🚀 Starting Medical Research Opportunities API...")
        print("📖 API Documentation will be available at: http://localhost:8000/docs")
        print("🔍 Health check: http://localhost:8000/health")
        print("⏹️  Press Ctrl+C to stop the server")
        print("-" * 60)
        
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        print(f"❌ Error starting API: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
