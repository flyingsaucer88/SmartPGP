"""
AEPGP Context Menu - MSI Installer Creator with Centralized Versioning

This script creates ONLY a Windows MSI installer package using cx_Freeze.
No standalone EXE is created - MSI only for professional deployment.

VERSION MANAGEMENT:
- The VERSION file is the single source of truth for version numbers
- Auto-increment: python create_msi.py bdist_msi --patch   (1.2.0 -> 1.2.1)
- Auto-increment: python create_msi.py bdist_msi --minor   (1.2.0 -> 1.3.0)
- Auto-increment: python create_msi.py bdist_msi --major   (1.2.0 -> 2.0.0)
- Manual build:   python create_msi.py bdist_msi           (uses current VERSION)

The VERSION file is automatically synced to install_menu.py before each build.
"""

import sys
import os
import re
from cx_Freeze import setup, Executable

# Version file location (single source of truth)
VERSION_FILE = "VERSION"

def read_version():
    """Read the current version from VERSION file."""
    if not os.path.exists(VERSION_FILE):
        print(f"ERROR: {VERSION_FILE} not found!")
        sys.exit(1)

    with open(VERSION_FILE, 'r') as f:
        version = f.read().strip()

    # Validate version format (major.minor.patch)
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        print(f"ERROR: Invalid version format in {VERSION_FILE}: {version}")
        print("Version must be in format: major.minor.patch (e.g., 1.2.0)")
        sys.exit(1)

    return version

def write_version(version):
    """Write the new version to VERSION file."""
    with open(VERSION_FILE, 'w') as f:
        f.write(version)
    print(f"[OK] Updated {VERSION_FILE}: {version}")

def increment_version(version, bump_type):
    """
    Increment version based on bump type.

    Args:
        version: Current version string (e.g., "1.2.0")
        bump_type: One of "major", "minor", "patch"

    Returns:
        New version string
    """
    major, minor, patch = map(int, version.split('.'))

    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'patch':
        patch += 1
    else:
        print(f"ERROR: Invalid bump type: {bump_type}")
        print("Valid options: --major, --minor, --patch")
        sys.exit(1)

    return f"{major}.{minor}.{patch}"

def sync_version_to_install_menu(version):
    """Update the CURRENT_VERSION in install_menu.py to match VERSION file."""
    install_menu_path = "install_menu.py"

    if not os.path.exists(install_menu_path):
        print(f"WARNING: {install_menu_path} not found, skipping sync")
        return

    with open(install_menu_path, 'r') as f:
        content = f.read()

    # Replace the CURRENT_VERSION line
    new_content = re.sub(
        r'CURRENT_VERSION = "[^"]*"',
        f'CURRENT_VERSION = "{version}"',
        content
    )

    with open(install_menu_path, 'w') as f:
        f.write(new_content)

    print(f"[OK] Synced version to {install_menu_path}: {version}")

# Check for version bump arguments
bump_type = None
if '--major' in sys.argv:
    bump_type = 'major'
    sys.argv.remove('--major')
elif '--minor' in sys.argv:
    bump_type = 'minor'
    sys.argv.remove('--minor')
elif '--patch' in sys.argv:
    bump_type = 'patch'
    sys.argv.remove('--patch')

# Read current version
current_version = read_version()
print(f"Current version: {current_version}")

# Auto-increment if requested
if bump_type:
    new_version = increment_version(current_version, bump_type)
    print(f"Incrementing version ({bump_type}): {current_version} -> {new_version}")
    write_version(new_version)
    current_version = new_version

# Sync version to all files
sync_version_to_install_menu(current_version)

# Application metadata
APP_NAME = "AEPGP Context Menu"
APP_VERSION = current_version
APP_DESCRIPTION = "Windows Explorer context menu for file encryption with AEPGP cards"
APP_AUTHOR = "AEPGP"
APP_COMPANY = "AEPGP"

# IMPORTANT: This upgrade code must remain the same across all versions
# It allows newer versions to automatically uninstall older ones
UPGRADE_CODE = "{A1B2C3D4-E5F6-4A5B-8C9D-0E1F2A3B4C5D}"

# Files to include in the MSI
include_files = [
    ('install_menu.py', 'install_menu.py'),
    ('uninstall_menu.py', 'uninstall_menu.py'),
    ('REINSTALL.bat', 'REINSTALL.bat'),  # Reinstall script for upgrading from old versions
    ('INSTALL.bat', 'INSTALL.bat'),  # Quick install script
    ('UNINSTALL.bat', 'UNINSTALL.bat'),  # Quick uninstall script
    ('handlers/card_utils.py', 'handlers/card_utils.py'),
    ('handlers/card_key_reader.py', 'handlers/card_key_reader.py'),
    ('handlers/encrypt_handler.py', 'handlers/encrypt_handler.py'),
    ('handlers/decrypt_handler.py', 'handlers/decrypt_handler.py'),
    ('handlers/generate_keys_handler.py', 'handlers/generate_keys_handler.py'),
    ('handlers/delete_keys_handler.py', 'handlers/delete_keys_handler.py'),
    ('handlers/import_pfx_handler.py', 'handlers/import_pfx_handler.py'),
    ('handlers/change_pin_handler.py', 'handlers/change_pin_handler.py'),
    ('handlers/rsa_crypto.py', 'handlers/rsa_crypto.py'),
    ('handlers/rsa_decrypt.py', 'handlers/rsa_decrypt.py'),
    ('handlers/debug_logger.py', 'handlers/debug_logger.py'),
    ('handlers/__init__.py', 'handlers/__init__.py'),
    ('requirements.txt', 'requirements.txt'),
    ('VERSION', 'VERSION'),  # Include VERSION file in MSI
]

# Add icon if it exists
if os.path.exists('aepgp_icon.ico'):
    include_files.append(('aepgp_icon.ico', 'aepgp_icon.ico'))

# Packages to include
packages = [
    'tkinter',
    'winreg',
    'ctypes',
    'subprocess',
    'threading',
    'smartcard',
    'cryptography',
]

# Build options (required for bdist_msi even though we're not creating standalone exe)
build_exe_options = {
    'packages': packages,
    'include_files': include_files,
    'excludes': ['test', 'unittest'],
    'optimize': 2,
}

# MSI-specific options
bdist_msi_options = {
    'add_to_path': False,
    'initial_target_dir': r'[ProgramFilesFolder]\AEPGP Context Menu',
    'install_icon': 'aepgp_icon.ico' if os.path.exists('aepgp_icon.ico') else None,
    'upgrade_code': UPGRADE_CODE,  # Enables automatic upgrade of older versions
    'target_name': 'AEPGP_Context_Menu',  # Consistent name for all versions
}

# Dummy executable configuration (required by cx_Freeze, but not used for standalone distribution)
# This is only used as part of the MSI build process
base = 'Win32GUI'  # No console window
icon = 'aepgp_icon.ico' if os.path.exists('aepgp_icon.ico') else None

exe = Executable(
    script='aepgp_installer.py',
    base=base,
    icon=icon,
    target_name='AEPGP_Installer.exe',
    shortcut_name='AEPGP Installer',
    shortcut_dir='ProgramMenuFolder',
)

# Setup configuration - MSI ONLY
# Run with: python create_msi.py bdist_msi
setup(
    name=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    author=APP_AUTHOR,
    options={
        'build_exe': build_exe_options,
        'bdist_msi': bdist_msi_options,
    },
    executables=[exe],
)

print("\n" + "="*70)
print("MSI Installer Creation")
print("="*70)
print(f"Application: {APP_NAME}")
print(f"Version: {APP_VERSION}")
print(f"Build Type: MSI ONLY (no standalone EXE)")
print(f"")
print(f"Version increment commands:")
print(f"  python create_msi.py bdist_msi --patch   (patch: x.x.X)")
print(f"  python create_msi.py bdist_msi --minor   (minor: x.X.0)")
print(f"  python create_msi.py bdist_msi --major   (major: X.0.0)")
print("="*70 + "\n")
