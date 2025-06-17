#!/usr/bin/env python3
"""
Frontend startup script for DSA Mentor
Streamlit application providing the user interface
"""

import streamlit as st
import subprocess
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_backend_status():
    """Check if backend server is running"""
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_frontend():
    """Start the Streamlit frontend application"""
    print("🎨 Starting DSA Mentor Frontend...")
    print("🌐 Frontend will be available at: http://localhost:8501")
    print("📡 Backend API: http://localhost:8000")
    print("-" * 60)
    
    # Check if backend is running
    if not check_backend_status():
        print("⚠️  Warning: Backend server is not running!")
        print("💡 Start the backend first: python start_backend.py")
        print("   Or run both with: python start_app.py")
        print("-" * 60)
    
    # Set environment variables
    os.environ.setdefault("PYTHONPATH", str(project_root))
    
    try:
        # Run Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "frontend/app.py",
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--theme.base=dark",
            "--theme.primaryColor=#FF6B6B",
            "--theme.backgroundColor=#0E1117",
            "--theme.secondaryBackgroundColor=#262730"
        ])
    except KeyboardInterrupt:
        print("\n👋 Frontend server stopped.")
    except Exception as e:
        print(f"❌ Error starting frontend server: {e}")
        print("💡 Make sure all dependencies are installed: uv sync")

if __name__ == "__main__":
    start_frontend()
