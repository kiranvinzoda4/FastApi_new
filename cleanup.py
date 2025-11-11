#!/usr/bin/env python3
import shutil
import os
from pathlib import Path

def cleanup_cache():
    """Remove pytest and Python cache folders"""
    root = Path(".")
    
    # Remove .pytest_cache
    pytest_cache = root / ".pytest_cache"
    if pytest_cache.exists():
        shutil.rmtree(pytest_cache)
        print("✅ Removed .pytest_cache")
    
    # Remove all __pycache__ folders
    for pycache in root.rglob("__pycache__"):
        if pycache.is_dir():
            shutil.rmtree(pycache)
            print(f"✅ Removed {pycache}")
    
    print("🧹 Cache cleanup complete")

if __name__ == "__main__":
    cleanup_cache()