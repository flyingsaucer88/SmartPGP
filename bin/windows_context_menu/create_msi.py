"""
AEPGP Context Menu - MSI Installer Creator

This script creates a Windows MSI installer package using cx_Freeze.
MSI installers provide a more professional installation experience.
"""

import sys
import os
from cx_Freeze import setup, Executable

# Application metadata
APP_NAME = "AEPGP Context Menu"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Windows Explorer context menu for file encryption with AEPGP cards"
APP_AUTHOR = "AEPGP"
APP_COMPANY = "AEPGP"

# Files to include
include_files = [
    ('install_menu.py', 'install_menu.py'),
    ('uninstall_menu.py', 'uninstall_menu.py'),
    ('handlers/card_utils.py', 'handlers/card_utils.py'),
    ('handlers/encrypt_handler.py', 'handlers/encrypt_handler.py'),
    ('handlers/decrypt_handler.py', 'handlers/decrypt_handler.py'),
    ('handlers/__init__.py', 'handlers/__init__.py'),
    ('requirements.txt', 'requirements.txt'),
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
]

# Build options
build_exe_options = {
    'packages': packages,
    'include_files': include_files,
    'excludes': ['test', 'unittest'],
    'optimize': 2,
}

# MSI options
bdist_msi_options = {
    'add_to_path': False,
    'initial_target_dir': r'[ProgramFilesFolder]\AEPGP Context Menu',
    'install_icon': 'aepgp_icon.ico' if os.path.exists('aepgp_icon.ico') else None,
}

# Executable configuration
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

# Setup configuration
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
