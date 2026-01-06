#!/usr/bin/env python
"""
Global test runner for Loom project

Usage:
  python run_tests.py                 # Run all tests
  python run_tests.py backend         # Run only backend tests
  python run_tests.py executor        # Run only executor tests
  python run_tests.py integration     # Run only integration tests
  python run_tests.py -v              # Verbose mode
  python run_tests.py --cov           # With coverage report
  python run_tests.py -k pattern      # Run tests matching pattern
  python run_tests.py -m async        # Run only async tests
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Run pytest with appropriate arguments based on user input."""
    
    # Determine which tests to run
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg == "backend":
            test_path = ["backend/tests"]
            print("Running backend tests only...")
        elif arg == "executor":
            test_path = ["executor/tests"]
            print("Running executor tests only...")
        elif arg == "integration":
            test_path = ["tests"]
            print("Running integration tests only...")
        elif arg in ["-h", "--help"]:
            print(__doc__)
            return 0
        else:
            # Pass through to pytest
            test_path = sys.argv[1:]
    else:
        test_path = ["backend/tests", "executor/tests", "tests"]
        print("Running all tests...")
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"] + test_path
    
    # Add any additional arguments from command line
    if len(sys.argv) > 2:
        cmd.extend(sys.argv[2:])
    
    # Run pytest
    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
