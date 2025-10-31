#!/usr/bin/env python3
import subprocess

print("Starting server...")
print("Server: http://127.0.0.1:8000")
print("Docs: http://127.0.0.1:8000/docs")
print("Health: http://127.0.0.1:8000/health")
print("\nPress Ctrl+C to stop\n")

try:
    subprocess.run([
        "venv\\Scripts\\python", "-m", "uvicorn", 
        "app.main:app", 
        "--reload", 
        "--port", "8000"
    ])
except KeyboardInterrupt:
    print("\nServer stopped")