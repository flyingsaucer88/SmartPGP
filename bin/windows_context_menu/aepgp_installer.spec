# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for AEPGP Context Menu Installer

This creates a single-file executable that bundles:
- Main GUI installer
- Install/Uninstall scripts
- Handler scripts
- All dependencies
"""

import os

block_cipher = None

a = Analysis(
    ['aepgp_installer.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('install_menu.py', '.'),
        ('uninstall_menu.py', '.'),
        ('handlers/*.py', 'handlers'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'winreg',
        'ctypes',
        'subprocess',
        'threading',
        'smartcard',
        'smartcard.System',
        'smartcard.Exceptions',
        'smartcard.util',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AEPGP_Installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='aepgp_icon.ico' if os.path.exists('aepgp_icon.ico') else None,  # Auto-detects icon
    version='version_info.txt' if os.path.exists('version_info.txt') else None,  # Auto-detects version
    uac_admin=False,  # We request elevation at runtime instead
    uac_uiaccess=False,
)
