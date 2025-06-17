#!/usr/bin/env python3
"""
Application startup script for DSA Mentor
Starts both backend (FastAPI) and frontend (Streamlit) servers
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path
from threading import Thread

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class DSAMentorApp:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        
    def start_backend(self):
        """Start the FastAPI backend server"""
        print("🚀 Starting Backend Server (FastAPI)...")
        try:
            self.backend_process = subprocess.Popen([
                sys.executable, "start_backend.py"
            ])
            return True
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the Streamlit frontend application"""
        print("🎨 Starting Frontend Application (Streamlit)...")
        # Wait a bit for backend to start
        time.sleep(3)
        
        try:
            self.frontend_process = subprocess.Popen([
                sys.executable, "start_frontend.py"
            ])
            return True
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False
    
    def wait_for_backend(self):
        """Wait for backend to be ready"""
        print("⏳ Waiting for backend to be ready...")
        max_attempts = 30
        
        for attempt in range(max_attempts):
            try:
                import requests
                response = requests.get("http://localhost:8000/health", timeout=1)
                if response.status_code == 200:
                    print("✅ Backend is ready!")
                    return True
            except:
                pass
            time.sleep(1)
            print(f"   Attempt {attempt + 1}/{max_attempts}...")
        
        print("❌ Backend failed to start properly")
        return False
    
    def stop_servers(self):
        """Stop both servers"""
        print("\n🛑 Stopping servers...")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            print("✅ Frontend stopped")
        
        if self.backend_process:
            self.backend_process.terminate()
            print("✅ Backend stopped")
    
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        self.stop_servers()
        sys.exit(0)
    
    def run(self):
        """Run the complete application"""
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        
        print("=" * 60)
        print("🎓 DSA MENTOR - AI-Powered Coding Coach")
        print("=" * 60)
        print("📚 Starting modular architecture...")
        print("🔧 Backend: FastAPI (http://localhost:8000)")
        print("🎨 Frontend: Streamlit (http://localhost:8501)")
        print("=" * 60)
        
        # Start backend
        if not self.start_backend():
            return
        
        # Wait for backend to be ready
        if not self.wait_for_backend():
            self.stop_servers()
            return
        
        # Start frontend
        if not self.start_frontend():
            self.stop_servers()
            return
        
        print("=" * 60)
        print("🎉 DSA Mentor is now running!")
        print("🌐 Open your browser and go to: http://localhost:8501")
        print("📖 API Documentation: http://localhost:8000/docs")
        print("🛑 Press Ctrl+C to stop both servers")
        print("=" * 60)
        
        try:
            # Wait for processes to complete
            while True:
                if self.backend_process and self.backend_process.poll() is not None:
                    print("❌ Backend process stopped unexpectedly")
                    break
                
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("❌ Frontend process stopped unexpectedly")
                    break
                
                time.sleep(1)
        
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_servers()

def main():
    """Main entry point"""
    app = DSAMentorApp()
    app.run()

if __name__ == "__main__":
    main()
