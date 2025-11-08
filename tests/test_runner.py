#!/usr/bin/env python3
"""
Test runner script for the DailyVeg API project.
Provides different test execution modes and reporting options.
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_tests(test_type="all", coverage=True, verbose=True, fail_fast=False):
    """Run tests with specified options"""
    
    cmd = ["poetry", "run", "pytest"]
    
    # Add test path based on type
    if test_type == "unit":
        cmd.append("tests/unit/")
    elif test_type == "integration":
        cmd.append("tests/integration/")
    elif test_type == "all":
        cmd.append("tests/")
    else:
        cmd.append(f"tests/{test_type}")
    
    # Add options
    if verbose:
        cmd.append("-v")
    
    if fail_fast:
        cmd.append("-x")
    
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=term-missing"])
    
    # Run the command
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode

def main():
    parser = argparse.ArgumentParser(description="Run tests for DailyVeg API")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "all"], 
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--no-coverage", 
        action="store_true",
        help="Disable coverage reporting"
    )
    parser.add_argument(
        "--quiet", 
        action="store_true",
        help="Run tests in quiet mode"
    )
    parser.add_argument(
        "--fail-fast", 
        action="store_true",
        help="Stop on first failure"
    )
    
    args = parser.parse_args()
    
    exit_code = run_tests(
        test_type=args.type,
        coverage=not args.no_coverage,
        verbose=not args.quiet,
        fail_fast=args.fail_fast
    )
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()