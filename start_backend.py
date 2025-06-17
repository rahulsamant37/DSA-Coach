#!/usr/bin/env python3
"""
Backend server startup script for DSA Mentor
FastAPI server providing AI-powered DSA coaching services
"""

import uvicorn
import os
from pathlib import Path

import os
from dotenv import load_dotenv
load_dotenv()
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')

# Add the project root to Python path
project_root = Path(__file__).parent
import sys
sys.path.insert(0, str(project_root))

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting DSA Mentor Backend Server...")
    print("📍 API Documentation will be available at: http://localhost:8000/docs")
    print("🔧 Backend API Base URL: http://localhost:8000")
    print("-" * 60)
    
    # Set environment variables
    os.environ.setdefault("PYTHONPATH", str(project_root))
    
    try:
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Backend server stopped.")
    except Exception as e:
        print(f"❌ Error starting backend server: {e}")
        print("💡 Make sure all dependencies are installed: uv sync")

if __name__ == "__main__":
    start_backend()
