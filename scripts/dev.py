#!/usr/bin/env python3
"""Development server script with auto-reload and debugging"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_dev_server():
    """Run development server with hot reload"""
    os.environ.setdefault("DEBUG", "True")
    os.environ.setdefault("LOG_LEVEL", "DEBUG")
    
    cmd = [
        "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload",
        "--reload-dir", "app",
        "--log-level", "debug"
    ]
    
    print("Starting development server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation: http://localhost:8000/docs")
    print("Health check: http://localhost:8000/health")
    
    try:
        subprocess.run(cmd, cwd=project_root)
    except KeyboardInterrupt:
        print("\nShutting down development server...")

if __name__ == "__main__":
    run_dev_server()