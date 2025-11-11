#!/usr/bin/env python3
import uvicorn

if __name__ == "__main__":
    print("Starting server...")
    print("Server: http://127.0.0.1:8000")
    print("Docs: http://127.0.0.1:8000/docs")
    print("Health: http://127.0.0.1:8000/health")
    print("\nPress Ctrl+C to stop\n")
    try:
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nServer stopped")