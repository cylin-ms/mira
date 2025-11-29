#!/usr/bin/env python3
"""
Setup script for the Assertion Analyzer package.

This script creates a virtual environment and installs dependencies.

Usage:
    python setup_env.py           # Create venv and install deps
    python setup_env.py --clean   # Remove existing venv first
"""

import os
import sys
import subprocess
import shutil
import argparse

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(PACKAGE_DIR, ".venv")
REQUIREMENTS_FILE = os.path.join(PACKAGE_DIR, "requirements.txt")


def run_command(cmd, description=None):
    """Run a command and handle errors."""
    if description:
        print(f"\n>> {description}")
    print(f"   $ {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"   ERROR: {result.stderr}")
        return False
    if result.stdout.strip():
        for line in result.stdout.strip().split('\n')[:5]:
            print(f"   {line}")
    return True


def create_venv():
    """Create a new virtual environment."""
    if os.path.exists(VENV_DIR):
        print(f"Virtual environment already exists at: {VENV_DIR}")
        return True
    
    print(f"Creating virtual environment at: {VENV_DIR}")
    result = subprocess.run(
        [sys.executable, "-m", "venv", VENV_DIR],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"ERROR creating venv: {result.stderr}")
        return False
    
    print("Virtual environment created successfully!")
    return True


def get_pip_path():
    """Get the path to pip in the virtual environment."""
    if sys.platform == "win32":
        return os.path.join(VENV_DIR, "Scripts", "pip.exe")
    return os.path.join(VENV_DIR, "bin", "pip")


def get_python_path():
    """Get the path to python in the virtual environment."""
    if sys.platform == "win32":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python")


def install_dependencies():
    """Install dependencies from requirements.txt."""
    pip_path = get_pip_path()
    
    if not os.path.exists(pip_path):
        print(f"ERROR: pip not found at {pip_path}")
        return False
    
    # Upgrade pip first
    run_command([pip_path, "install", "--upgrade", "pip"], "Upgrading pip")
    
    # Install requirements
    if os.path.exists(REQUIREMENTS_FILE):
        success = run_command(
            [pip_path, "install", "-r", REQUIREMENTS_FILE],
            "Installing dependencies from requirements.txt"
        )
        if not success:
            return False
    else:
        print(f"WARNING: {REQUIREMENTS_FILE} not found")
    
    return True


def clean_venv():
    """Remove the virtual environment."""
    if os.path.exists(VENV_DIR):
        print(f"Removing existing virtual environment: {VENV_DIR}")
        shutil.rmtree(VENV_DIR)
        print("Removed!")
    else:
        print("No virtual environment to remove.")


def print_usage_instructions():
    """Print instructions for using the virtual environment."""
    python_path = get_python_path()
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    print("\nTo use the Assertion Analyzer:\n")
    
    if sys.platform == "win32":
        print("Option 1: Use the run script (RECOMMENDED)")
        print(f"  PS> cd {PACKAGE_DIR}")
        print(f'  PS> .\\run.ps1 "Your assertion here"')
        print()
        print("Option 2: Activate venv and run")
        print(f"  PS> cd {PACKAGE_DIR}")
        print(f"  PS> .venv\\Scripts\\Activate.ps1")
        print(f"  PS> $env:PYTHONPATH = (Split-Path -Parent (pwd))")
        print(f'  PS> python -m assertion_analyzer "Your assertion here"')
    else:
        print("Option 1: Use the run script (RECOMMENDED)")
        print(f"  $ cd {PACKAGE_DIR}")
        print(f'  $ ./run.sh "Your assertion here"')
        print()
        print("Option 2: Activate venv and run")
        print(f"  $ cd {PACKAGE_DIR}")
        print(f"  $ source .venv/bin/activate")
        print(f"  $ export PYTHONPATH=$(dirname $(pwd))")
        print(f'  $ python -m assertion_analyzer "Your assertion here"')
    
    print()
    print("Quick test (no WBP generation):")
    if sys.platform == "win32":
        print(f'  PS> .\\run.ps1 "Test assertion" -NoExamples -Quiet')
    else:
        print(f'  $ ./run.sh "Test assertion" --no-examples --quiet')
    print()
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Set up virtual environment for Assertion Analyzer"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove existing virtual environment before creating new one"
    )
    args = parser.parse_args()
    
    print("=" * 60)
    print("Assertion Analyzer - Environment Setup")
    print("=" * 60)
    
    if args.clean:
        clean_venv()
    
    if not create_venv():
        print("\nFailed to create virtual environment!")
        return 1
    
    if not install_dependencies():
        print("\nFailed to install dependencies!")
        return 1
    
    print_usage_instructions()
    return 0


if __name__ == "__main__":
    sys.exit(main())
