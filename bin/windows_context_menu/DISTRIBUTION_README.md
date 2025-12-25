# AEPGP Context Menu - Distribution Guide

## Quick Start for Developers

### To Build the Executable:

**On Windows:**
```cmd
cd bin/windows_context_menu
build_exe.bat
```

**Result:** `dist/AEPGP_Installer.exe` (~15-25 MB)

### To Distribute:

**Option 1 - Single File (Recommended):**
- Distribute just: `AEPGP_Installer.exe`
- Users don't need Python installed!

**Option 2 - Full Package:**
- Include: executable + user documentation + support info

## What Users Need

### Before Installation:
1. **Windows 10 or 11**
2. **GnuPG** - Download from https://www.gpg4win.org/
3. **AmbiSecure AEPGP token** (ATR: 3B D5 18 FF 81 B1 FE 45 1F C3 80 73 C8 21 10 6F)
4. **USB smart card reader**

### User Installation Steps:
1. Double-click `AEPGP_Installer.exe`
2. Click "Install"
3. Approve Administrator elevation
4. **ONE-TIME SETUP:** Initialize card with GnuPG:
   ```cmd
   gpg --card-edit
   > admin
   > generate
   ```

### User Usage:
- **Encrypt:** Right-click file → "Encrypt with AEPGP"
- **Decrypt:** Right-click `.gpg` file → "Decrypt with AEPGP"
- **Windows 11:** Click "Show more options" first

## Files in This Directory

### For End Users (Distribute These):
- **`AEPGP_Installer.exe`** ← Built executable (in `dist/` after building)

### For Developers (Keep These):
- **`aepgp_installer.py`** - GUI installer source code
- **`install_menu.py`** - Installation script
- **`uninstall_menu.py`** - Uninstallation script
- **`handlers/`** - Handler scripts for encrypt/decrypt
- **`aepgp_installer.spec`** - PyInstaller specification
- **`build_exe.bat`** - Windows build script
- **`build_exe.py`** - Python build script
- **`requirements.txt`** - Python dependencies
- **`BUILD_INSTRUCTIONS.md`** - Detailed build guide
- **`AEPGP_CHANGES.md`** - Customization documentation

### Documentation:
- **`BUILD_INSTRUCTIONS.md`** - How to build the executable
- **`AEPGP_CHANGES.md`** - Technical details about customizations
- **`README.md`** - Full technical documentation
- **`QUICKSTART.md`** - Quick reference guide

## Key Features

### AmbiSecure Token Detection
✅ Only accepts tokens with ATR: `3B D5 18 FF 81 B1 FE 45 1F C3 80 73 C8 21 10 6F`

### AEPGP Branding
✅ All user-facing text uses "AEPGP" (not "SmartPGP")

### Easy Distribution
✅ Single `.exe` file - no Python required for end users

### GUI Installer
✅ User-friendly graphical interface
✅ Install and uninstall from same executable
✅ Shows installation status

## Build Process Overview

```
Source Code (Python)
       ↓
  PyInstaller
       ↓
Standalone .exe (15-25 MB)
       ↓
   Distribute
       ↓
End Users (no Python needed!)
```

## Testing Checklist

Before distributing to end users:

- [ ] Build succeeds without errors
- [ ] Executable runs on Windows 10
- [ ] Executable runs on Windows 11
- [ ] Installation works (creates registry entries)
- [ ] Encryption works with AmbiSecure token
- [ ] Decryption works with AmbiSecure token
- [ ] Non-AmbiSecure cards are rejected
- [ ] Uninstallation works (removes registry entries)
- [ ] **CRITICAL:** Test on PC without Python installed
- [ ] Antivirus doesn't flag it (or document workaround)

## Support Information

### For Build Issues:
- See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)

### For Technical Details:
- See [AEPGP_CHANGES.md](AEPGP_CHANGES.md)

### For User Instructions:
- See [QUICKSTART.md](QUICKSTART.md)

## Version History

### Version 1.0 (Current)
- Initial AEPGP release
- AmbiSecure ATR-specific detection
- Full AEPGP rebranding
- GUI installer
- Standalone executable support

## License

Based on SmartPGP project by ANSSI (GPL v2)
Customized for AEPGP with AmbiSecure token support

## Quick Reference

| Task | Command |
|------|---------|
| Build executable | `build_exe.bat` |
| Test installation | Run `dist/AEPGP_Installer.exe` |
| Distribute | Copy `dist/AEPGP_Installer.exe` |
| User encrypts file | Right-click → "Encrypt with AEPGP" |
| User decrypts file | Right-click → "Decrypt with AEPGP" |

## Deployment Workflow

```
1. Developer builds:
   └─> build_exe.bat

2. Developer tests:
   └─> dist/AEPGP_Installer.exe

3. Developer distributes:
   └─> Copy AEPGP_Installer.exe to users

4. User installs:
   └─> Double-click AEPGP_Installer.exe
   └─> Click "Install"

5. User initializes (ONE-TIME):
   └─> gpg --card-edit
   └─> generate keys

6. User encrypts/decrypts:
   └─> Right-click files
```

## File Size

- **Executable:** ~15-25 MB (bundled with Python + dependencies)
- **Source code only:** ~100 KB
- **Why so large?** Includes entire Python interpreter and all libraries for standalone operation

## Distribution Channels

Recommended ways to distribute:

1. **Direct download:** Host on your website/server
2. **USB drive:** Pre-load on USB sticks for users
3. **Network share:** Company network location
4. **Email:** Small enough to email (if policies allow)
5. **Package manager:** Create installer package (MSI/NSIS)

## Security Notes

- **Code signing:** Recommended for production (reduces antivirus false positives)
- **Checksum:** Provide SHA256 hash for verification
- **Antivirus:** Test with Windows Defender and VirusTotal
- **Updates:** Rebuild and redistribute when code changes

## Customization

To customize branding further:

1. **Add icon:** Edit `aepgp_installer.spec` (line with `icon=None`)
2. **Change name:** Edit `aepgp_installer.spec` (line with `name=`)
3. **Modify GUI:** Edit `aepgp_installer.py`
4. **Rebuild:** Run `build_exe.bat`

## End User Experience

1. User downloads: `AEPGP_Installer.exe`
2. User runs executable (no Python needed)
3. GUI appears with Install/Uninstall buttons
4. User clicks Install → UAC prompt → Installed
5. Context menu entries appear in Explorer
6. User initializes card with GnuPG (one-time)
7. User right-clicks files to encrypt/decrypt

Simple, clean, professional!
