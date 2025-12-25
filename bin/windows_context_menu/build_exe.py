"""
AEPGP Context Menu - Python Build Script

This script builds a standalone executable using PyInstaller.
Alternative to build_exe.bat for users who prefer Python scripts.
"""

import sys
import os
import subprocess
import shutil


def check_python():
    """Check Python version"""
    print("[1/5] Checking Python installation...")
    print(f"Python {sys.version}")
    if sys.version_info < (3, 7):
        print("ERROR: Python 3.7 or later is required")
        return False
    return True


def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        print(f"ERROR: Failed to install {package}")
        return False


def check_dependencies():
    """Check and install required dependencies"""
    print("\n[2/5] Checking PyInstaller...")
    try:
        import PyInstaller
        print("PyInstaller is already installed")
    except ImportError:
        print("PyInstaller not found. Installing...")
        if not install_package("pyinstaller"):
            return False

    print("\n[3/5] Checking pyscard...")
    try:
        import smartcard
        print("pyscard is already installed")
    except ImportError:
        print("pyscard not found. Installing...")
        if not install_package("pyscard"):
            return False

    return True


def clean_build():
    """Clean previous build artifacts"""
    print("\n[4/5] Cleaning previous build...")
    dirs_to_remove = ["build", "dist", "__pycache__", "handlers/__pycache__"]

    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}")

    return True


def build_executable():
    """Build the executable using PyInstaller"""
    print("\n[5/5] Building executable...")
    print("This may take a few minutes...\n")

    try:
        subprocess.check_call([
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            "aepgp_installer.spec"
        ])
        return True
    except subprocess.CalledProcessError:
        print("\nBUILD FAILED")
        return False


def main():
    """Main build process"""
    print("=" * 60)
    print("AEPGP Context Menu - Build Script")
    print("=" * 60)
    print()

    # Check Python
    if not check_python():
        input("\nPress Enter to exit...")
        sys.exit(1)

    # Check and install dependencies
    if not check_dependencies():
        input("\nPress Enter to exit...")
        sys.exit(1)

    # Clean previous build
    if not clean_build():
        input("\nPress Enter to exit...")
        sys.exit(1)

    # Build executable
    if not build_executable():
        print("\n" + "=" * 60)
        print("BUILD FAILED")
        print("=" * 60)
        input("\nPress Enter to exit...")
        sys.exit(1)

    # Success
    print("\n" + "=" * 60)
    print("BUILD SUCCESSFUL!")
    print("=" * 60)
    print()
    print("The executable has been created:")
    print("  dist/AEPGP_Installer.exe")
    print()

    # Get file size
    exe_path = "dist/AEPGP_Installer.exe"
    if os.path.exists(exe_path):
        size = os.path.getsize(exe_path)
        size_mb = size / (1024 * 1024)
        print(f"File size: {size_mb:.2f} MB")
    print()
    print("You can now distribute this single .exe file to users.")
    print("Users do NOT need Python installed to run it.")
    print()

    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
