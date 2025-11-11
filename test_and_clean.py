#!/usr/bin/env python3
import subprocess
import sys
from cleanup import cleanup_cache

def run_tests_and_cleanup():
    """Run tests and automatically cleanup cache folders"""
    print("🧪 Running tests...")
    
    # Run pytest
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/", "--tb=line", "--no-header", 
        "-q", "--color=yes", "--disable-warnings"
    ])
    
    # Cleanup cache regardless of test results
    print("\n🧹 Cleaning up cache folders...")
    cleanup_cache()
    
    return result.returncode

if __name__ == "__main__":
    exit_code = run_tests_and_cleanup()
    sys.exit(exit_code)