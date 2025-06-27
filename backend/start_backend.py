#!/usr/bin/env python
"""
Startup script for Prime Time Medical Research Opportunities API Backend
"""
import sys
import os
from pathlib import Path

# Add project root and src directories to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

if __name__ == "__main__":
    try:
        import uvicorn
        
        print("🚀 Starting Prime Time Medical Research Opportunities API Backend...")
        print("📖 API Documentation will be available at: http://localhost:8000/docs")
        print("🔍 Health check: http://localhost:8000/health")
        print("⏹️  Press Ctrl+C to stop the server")
        print("-" * 60)
        
        uvicorn.run(
            "main:app",
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
