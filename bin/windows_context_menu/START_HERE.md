# 🚀 AEPGP Context Menu - START HERE

Welcome! This is your complete guide to the AEPGP Context Menu project.

## ⚡ Quick Start (I Just Want to Build It!)

**On Windows:**
```cmd
cd windows_context_menu
build_exe.bat
```

**Done!** Find your installer at: `dist/AEPGP_Installer.exe`

Distribute this single .exe file to users. They don't need Python!

## 📖 Documentation Index

### For First-Time Users
👉 **[COMPLETE_BUILD_GUIDE.md](COMPLETE_BUILD_GUIDE.md)** - Everything in one place
- Building executables
- Adding icons
- Version information
- MSI installers
- Complete workflow

### Quick References
- **[USER_GUIDE.txt](USER_GUIDE.txt)** - Give this to end users
- **[DISTRIBUTION_README.md](DISTRIBUTION_README.md)** - Distribution overview
- **[AEPGP_CHANGES.md](AEPGP_CHANGES.md)** - AmbiSecure customizations

### Building & Packaging
- **[BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)** - Build standalone .exe
- **[MSI_INSTALLER_GUIDE.md](MSI_INSTALLER_GUIDE.md)** - Build MSI installer
- **[CREATE_ICON.md](CREATE_ICON.md)** - Add custom icon
- **[UPDATE_VERSION.md](UPDATE_VERSION.md)** - Update version info

### Technical Documentation
- **[README.md](README.md)** - Full technical details
- **[QUICKSTART.md](QUICKSTART.md)** - Quick reference guide

## 🎯 What Do You Want to Do?

### I want to build the installer
➡️ Run: `build_exe.bat`
➡️ Or read: [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)

### I want to add my company icon
➡️ Read: [CREATE_ICON.md](CREATE_ICON.md)
➡️ Then: Place `aepgp_icon.ico` in this folder
➡️ Then: Run `build_exe.bat`

### I want to update the version number
➡️ Edit: `version_info.txt`
➡️ Read: [UPDATE_VERSION.md](UPDATE_VERSION.md)
➡️ Then: Run `build_exe.bat`

### I want to create an MSI installer
➡️ Run: `build_msi.bat`
➡️ Or read: [MSI_INSTALLER_GUIDE.md](MSI_INSTALLER_GUIDE.md)

### I want to distribute to users
➡️ Read: [DISTRIBUTION_README.md](DISTRIBUTION_README.md)
➡️ Give users: `dist/AEPGP_Installer.exe` + `USER_GUIDE.txt`

### I need to customize the code
➡️ Read: [AEPGP_CHANGES.md](AEPGP_CHANGES.md) (technical details)
➡️ Read: [README.md](README.md) (full documentation)

## 📁 File Structure

```
windows_context_menu/
│
├── 📄 START_HERE.md              ← You are here!
├── 📘 COMPLETE_BUILD_GUIDE.md    ← Everything in one place
│
├── Build Scripts
│   ├── build_exe.bat             ← Build standalone .exe
│   ├── build_exe.py              ← Python build script
│   ├── build_msi.bat             ← Build MSI installer
│   └── create_msi.py             ← MSI configuration
│
├── Configuration
│   ├── aepgp_installer.spec      ← PyInstaller config
│   ├── version_info.txt          ← Version metadata
│   └── requirements.txt          ← Dependencies
│
├── Source Code
│   ├── aepgp_installer.py        ← GUI installer
│   ├── install_menu.py           ← Installation logic
│   ├── uninstall_menu.py         ← Uninstallation logic
│   └── handlers/                 ← Encryption/decryption handlers
│       ├── card_utils.py         ← AmbiSecure card detection
│       ├── encrypt_handler.py    ← File encryption
│       └── decrypt_handler.py    ← File decryption
│
├── Documentation
│   ├── USER_GUIDE.txt            ← For end users
│   ├── BUILD_INSTRUCTIONS.md     ← Build .exe
│   ├── MSI_INSTALLER_GUIDE.md    ← Build MSI
│   ├── CREATE_ICON.md            ← Add icon
│   ├── UPDATE_VERSION.md         ← Update version
│   ├── DISTRIBUTION_README.md    ← Distribution guide
│   ├── AEPGP_CHANGES.md          ← Technical changes
│   ├── README.md                 ← Full documentation
│   └── QUICKSTART.md             ← Quick reference
│
└── Output (after building)
    └── dist/
        ├── AEPGP_Installer.exe   ← Standalone installer
        └── *.msi                 ← MSI installer (if built)
```

## 🎨 Key Features

### AmbiSecure Token Detection
✅ Only accepts AmbiSecure tokens with ATR: `3B D5 18 FF 81 B1 FE 45 1F C3 80 73 C8 21 10 6F`

### AEPGP Branding
✅ All user-facing text uses "AEPGP" (not "SmartPGP")

### Professional Distribution
✅ Standalone .exe (no Python required for users)
✅ MSI installer (enterprise-ready)
✅ Icon support
✅ Version information
✅ Complete documentation

## 🔧 Prerequisites

### For Building (Developer)
- Windows 10 or 11
- Python 3.7+
- Run: `pip install pyinstaller pyscard cx_Freeze`

### For End Users
- Windows 10 or 11
- GnuPG (from https://www.gpg4win.org/)
- AmbiSecure AEPGP card
- USB smart card reader
- **No Python required!**

## 🚀 Build Commands

### Build Standalone EXE
```cmd
build_exe.bat
```
Output: `dist/AEPGP_Installer.exe` (~15-25 MB)

### Build MSI Installer
```cmd
build_msi.bat
```
Output: `dist/AEPGP_ContextMenu-1.0.0-win64.msi` (~20-35 MB)

### Build Both
```cmd
build_exe.bat
build_msi.bat
```

## 📦 What to Distribute

### Option 1: Standalone (Simple)
```
AEPGP_Installer.exe
```

### Option 2: With Documentation
```
AEPGP_Package/
├── AEPGP_Installer.exe
└── USER_GUIDE.txt
```

### Option 3: Complete Package
```
AEPGP_Package/
├── AEPGP_Installer.exe       # Standalone version
├── AEPGP_ContextMenu-1.0.0.msi  # MSI version
├── USER_GUIDE.txt            # User documentation
└── README.txt                # Your instructions
```

## 🎯 Common Tasks

| Task | Action |
|------|--------|
| Build installer | `build_exe.bat` |
| Add icon | Place `aepgp_icon.ico`, rebuild |
| Change version | Edit `version_info.txt`, rebuild |
| Create MSI | `build_msi.bat` |
| Test installer | Run `dist/AEPGP_Installer.exe` |
| Distribute | Copy `dist/AEPGP_Installer.exe` |

## 🆘 Need Help?

### For Building Issues
➡️ Read: [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)

### For Distribution Questions
➡️ Read: [DISTRIBUTION_README.md](DISTRIBUTION_README.md)

### For Technical Details
➡️ Read: [AEPGP_CHANGES.md](AEPGP_CHANGES.md)

### For End User Support
➡️ Give them: [USER_GUIDE.txt](USER_GUIDE.txt)

### For Everything Else
➡️ Read: [COMPLETE_BUILD_GUIDE.md](COMPLETE_BUILD_GUIDE.md)

## ✅ Quick Checklist

Before distributing:

- [ ] Built latest version (`build_exe.bat`)
- [ ] Tested on Windows 10
- [ ] Tested on Windows 11
- [ ] Tested with AmbiSecure token
- [ ] Verified ATR filtering works
- [ ] Tested on PC without Python
- [ ] Updated USER_GUIDE.txt with support info
- [ ] Created README for distribution package
- [ ] Scanned for viruses
- [ ] Named files with version number

## 🎉 You're Ready!

That's it! You have everything you need to:
- ✅ Build professional installers
- ✅ Add custom branding
- ✅ Distribute to users
- ✅ Support enterprise deployment

**Next Step:** Run `build_exe.bat` and start distributing!

---

**Need a quick refresher?**
➡️ [COMPLETE_BUILD_GUIDE.md](COMPLETE_BUILD_GUIDE.md) has everything

**Questions?**
➡️ Check the documentation files above

**Ready to distribute?**
➡️ Run `build_exe.bat` now!

---

Good luck with your AEPGP deployment! 🚀
