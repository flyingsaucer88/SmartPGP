# AEPGP Context Menu - Build Instructions

This document explains how to build a standalone executable for easy distribution.

## Overview

The AEPGP Context Menu can be distributed as a single `.exe` file that:
- Provides a GUI for installation/uninstallation
- Bundles all Python dependencies
- **Does not require users to install Python**
- Requests Administrator privileges when needed
- Includes all handler scripts

## Prerequisites for Building

### Required Software
1. **Windows 10 or 11** (for building Windows executables)
2. **Python 3.7 or later** installed
3. **pip** (Python package manager)

### Required Python Packages
- `pyscard` - Smart card communication
- `pyinstaller` - Executable builder

Install with:
```cmd
pip install -r requirements.txt
```

## Building the Executable

### Method 1: Using the Batch File (Easiest)

1. Open Command Prompt (no admin required for building)

2. Navigate to the `windows_context_menu` directory:
   ```cmd
   cd path\to\SmartPGP\bin\windows_context_menu
   ```

3. Run the build script:
   ```cmd
   build_exe.bat
   ```

4. Wait for the build to complete (typically 1-3 minutes)

5. Find the executable in:
   ```
   dist\AEPGP_Installer.exe
   ```

### Method 2: Using the Python Script

1. Open Command Prompt

2. Navigate to the directory:
   ```cmd
   cd path\to\SmartPGP\bin\windows_context_menu
   ```

3. Run the Python build script:
   ```cmd
   python build_exe.py
   ```

4. The executable will be created in `dist\AEPGP_Installer.exe`

### Method 3: Manual PyInstaller Command

For advanced users who want more control:

```cmd
pyinstaller --clean aepgp_installer.spec
```

## What Gets Built

The build process creates:

### During Build:
- `build/` - Temporary build files (auto-deleted)
- `dist/AEPGP_Installer.exe` - **Final executable** (~15-25 MB)

### What's Bundled:
The executable includes:
- ✅ GUI installer application
- ✅ Install/uninstall scripts
- ✅ Handler scripts (encrypt_handler.py, decrypt_handler.py, card_utils.py)
- ✅ Python interpreter
- ✅ All Python dependencies (pyscard, tkinter, etc.)
- ✅ Required DLLs

## Testing the Executable

Before distribution, test the executable:

1. **Test Installation:**
   ```cmd
   dist\AEPGP_Installer.exe
   ```
   - Click "Install"
   - Verify context menu appears when right-clicking files

2. **Test with AmbiSecure Token:**
   - Insert your AmbiSecure token (ATR: 3B D5 18 FF 81 B1 FE 45 1F C3 80 73 C8 21 10 6F)
   - Right-click a file → "Encrypt with AEPGP"
   - Verify encryption works

3. **Test Uninstallation:**
   - Run the executable again
   - Click "Uninstall"
   - Verify context menu items are removed

4. **Test on Clean System:**
   - Test on a Windows PC **without Python installed**
   - This ensures the executable is truly standalone

## Distribution

### What to Distribute

**Single File Distribution:**
```
AEPGP_Installer.exe  (from dist/ folder)
```

That's it! Users only need this one file.

### Optional Additional Files:
If you want to provide more context, create a distribution package:

```
AEPGP_Package/
├── AEPGP_Installer.exe        # Main installer
├── README_FOR_USERS.txt       # Simple user instructions
└── SUPPORT.txt                # Support contact information
```

### Recommended User Instructions

Create a simple `README_FOR_USERS.txt`:

```
AEPGP Context Menu Installer
=============================

REQUIREMENTS:
- Windows 10 or Windows 11
- AmbiSecure AEPGP token
- USB smart card reader
- GnuPG (download from https://www.gpg4win.org/)

INSTALLATION:
1. Double-click AEPGP_Installer.exe
2. Click "Install"
3. Click "Yes" when prompted for Administrator privileges
4. Close the installer

FIRST-TIME SETUP (ONE-TIME ONLY):
1. Insert your AEPGP card
2. Open Command Prompt
3. Run: gpg --card-edit
4. Type: admin
5. Type: generate
6. Follow prompts to create your encryption keys

USAGE:
- Encrypt: Right-click any file → "Encrypt with AEPGP"
- Decrypt: Right-click .gpg file → "Decrypt with AEPGP"
- On Windows 11: Click "Show more options" first

UNINSTALL:
1. Double-click AEPGP_Installer.exe
2. Click "Uninstall"
```

## Troubleshooting Build Issues

### Issue: "PyInstaller not found"
**Solution:**
```cmd
pip install pyinstaller
```

### Issue: "pyscard not found"
**Solution:**
```cmd
pip install pyscard
```

### Issue: "Module not found" errors during build
**Solution:**
The `.spec` file includes all necessary modules. If you get errors:
1. Install the missing package: `pip install <package_name>`
2. Add to `hiddenimports` in `aepgp_installer.spec`
3. Rebuild: `pyinstaller --clean aepgp_installer.spec`

### Issue: Executable is too large
**Solution:**
Current size (~15-25 MB) is normal for bundled Python applications.
To reduce size:
- PyInstaller already uses UPX compression
- Could exclude unused modules (advanced - may break functionality)

### Issue: Antivirus flags the executable
**Solution:**
- This is common with PyInstaller executables
- You can:
  - Code-sign the executable (requires certificate)
  - Submit to antivirus vendors as false positive
  - Have users whitelist the file

### Issue: "Failed to execute script"
**Solution:**
- Rebuild with `--debug=all` flag to see detailed error
- Check that all files are included in the `.spec` file

## Advanced Customization

### Adding an Icon

1. Create or obtain a `.ico` file (e.g., `aepgp_icon.ico`)

2. Edit `aepgp_installer.spec`:
   ```python
   exe = EXE(
       ...
       icon='aepgp_icon.ico',  # Add this line
       ...
   )
   ```

3. Rebuild

### Adding Version Information

1. Create a version file `version_info.txt`:
   ```
   VSVersionInfo(
     ffi=FixedFileInfo(
       filevers=(1, 0, 0, 0),
       prodvers=(1, 0, 0, 0),
       ...
     ),
     ...
   )
   ```

2. Reference in `.spec` file

3. Rebuild

### Changing Executable Name

Edit `aepgp_installer.spec`:
```python
exe = EXE(
    ...
    name='YourCustomName',  # Change this
    ...
)
```

## File Size Optimization

Current executable size: ~15-25 MB

**Why so large?**
- Bundles entire Python interpreter (~5 MB)
- Includes all dependencies (pyscard, tkinter, etc.)
- Includes Windows DLLs

**Cannot significantly reduce without:**
- Removing features
- Not bundling Python (requires users to install Python)
- Advanced techniques that may break functionality

## Security Considerations

### Code Signing (Optional but Recommended)

For production distribution:

1. **Obtain a code signing certificate**
   - From trusted CA (DigiCert, Sectigo, etc.)
   - Cost: $100-500/year

2. **Sign the executable:**
   ```cmd
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist\AEPGP_Installer.exe
   ```

3. **Benefits:**
   - Users see verified publisher
   - Reduces antivirus false positives
   - Establishes trust

### Antivirus Scanning

Before distribution:
1. Scan with Windows Defender
2. Upload to VirusTotal.com
3. Address any false positives with vendors

## Updating the Executable

When you make changes to the code:

1. Make your changes to the Python files
2. Test the Python version first
3. Rebuild the executable:
   ```cmd
   build_exe.bat
   ```
4. Test the new executable
5. Distribute the updated `AEPGP_Installer.exe`

## Build Script Details

### What `build_exe.bat` does:

1. Checks Python installation
2. Installs PyInstaller (if needed)
3. Installs pyscard (if needed)
4. Cleans previous build artifacts
5. Runs PyInstaller with the spec file
6. Shows build results

### What `aepgp_installer.spec` includes:

- **Entry point:** `aepgp_installer.py`
- **Data files:**
  - `install_menu.py`
  - `uninstall_menu.py`
  - `handlers/*.py`
- **Dependencies:**
  - tkinter (GUI)
  - winreg (registry access)
  - smartcard (card detection)
  - All other required modules

## Support

For build issues:
1. Check this document
2. Review error messages
3. Check PyInstaller documentation: https://pyinstaller.org/
4. Check pyscard documentation: https://pyscard.sourceforge.io/

## License

The built executable is derived from the SmartPGP project (GPL v2) with AEPGP-specific customizations.
When distributing, ensure compliance with the GPL v2 license.
