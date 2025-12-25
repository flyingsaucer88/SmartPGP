# AEPGP Context Menu - Complete Build & Distribution Guide

## 🎉 Everything You Need to Know

This guide covers all four enhancements you requested:
1. ✅ User Guide
2. ✅ Icon Support
3. ✅ Version Information
4. ✅ MSI Installer

## 📦 What's Included

Your `windows_context_menu/` folder now contains:

### Build Scripts
- `build_exe.bat` - Build standalone .exe
- `build_exe.py` - Python build script (alternative)
- `build_msi.bat` - Build MSI installer
- `create_msi.py` - MSI configuration

### Configuration Files
- `aepgp_installer.spec` - PyInstaller configuration (auto-detects icon & version)
- `version_info.txt` - Version metadata for .exe
- `requirements.txt` - Python dependencies

### Documentation
- `USER_GUIDE.txt` - **NEW!** End-user instructions
- `CREATE_ICON.md` - **NEW!** How to create/add icon
- `UPDATE_VERSION.md` - **NEW!** How to update version info
- `MSI_INSTALLER_GUIDE.md` - **NEW!** Complete MSI guide
- `BUILD_INSTRUCTIONS.md` - Detailed build instructions
- `DISTRIBUTION_README.md` - Distribution overview
- `AEPGP_CHANGES.md` - Technical customizations

### Source Code
- `aepgp_installer.py` - GUI installer
- `install_menu.py` - Installation script
- `uninstall_menu.py` - Uninstallation script
- `handlers/` - Encryption/decryption handlers

## 🚀 Quick Start

### Build Standalone EXE (Easiest)

```cmd
cd windows_context_menu
build_exe.bat
```

**Output:** `dist/AEPGP_Installer.exe` (~15-25 MB)

### Build MSI Installer (Professional)

```cmd
cd windows_context_menu
build_msi.bat
```

**Output:** `dist/AEPGP Context Menu-1.0.0-win64.msi` (~20-35 MB)

### Build Both

```cmd
build_exe.bat
build_msi.bat
```

Now you have both formats to distribute!

## 🎨 Adding Custom Branding

### 1. Add Your Icon

**Option A: Quick (Online Converter)**
1. Create 256x256 PNG image
2. Convert to .ico at https://convertio.co/png-ico/
3. Save as `aepgp_icon.ico`
4. Rebuild: `build_exe.bat`

**Option B: Using GIMP**
1. Create 256x256 image in GIMP
2. Export as `aepgp_icon.ico` (check all sizes: 16, 32, 48, 256)
3. Rebuild

See [CREATE_ICON.md](CREATE_ICON.md) for detailed instructions.

### 2. Update Version Information

Edit `version_info.txt`:

```python
filevers=(1, 0, 0, 0),  # Change to (1, 1, 0, 0) for version 1.1
prodvers=(1, 0, 0, 0),  # Change to (1, 1, 0, 0)
...
StringStruct(u'FileVersion', u'1.0.0.0'),  # Change to '1.1.0.0'
StringStruct(u'CompanyName', u'Your Company'),  # Customize
StringStruct(u'LegalCopyright', u'Copyright 2025 Your Company'),  # Customize
```

Then rebuild: `build_exe.bat`

See [UPDATE_VERSION.md](UPDATE_VERSION.md) for detailed instructions.

### 3. Customize Company Information

**For EXE:**
Edit `version_info.txt`:
- Company Name
- Copyright
- Product Name

**For MSI:**
Edit `create_msi.py`:
```python
APP_AUTHOR = "Your Company"
APP_COMPANY = "Your Company"
```

## 📚 User Documentation

### USER_GUIDE.txt (NEW!)

A comprehensive user guide that explains:
- What AEPGP is
- System requirements
- Installation steps
- First-time setup (GnuPG initialization)
- How to encrypt files
- How to decrypt files
- Troubleshooting
- FAQ

**Distribution:** Include `USER_GUIDE.txt` with your installer for users.

## 📋 Distribution Options

### Option 1: Standalone EXE Only (Simplest)

**What to distribute:**
```
AEPGP_Installer.exe
```

**Pros:**
- Single file
- Smallest package
- Easy distribution
- No installation wizard

**Best for:**
- Quick deployment
- Tech-savvy users
- Small organizations

### Option 2: MSI Installer Only (Professional)

**What to distribute:**
```
AEPGP_ContextMenu-1.0.0-win64.msi
```

**Pros:**
- Professional installer wizard
- Appears in Add/Remove Programs
- Group Policy deployable
- Repair & uninstall features

**Best for:**
- Enterprise environments
- IT departments
- Large-scale deployment

### Option 3: Complete Package (Recommended)

**What to distribute:**
```
AEPGP_Package/
├── AEPGP_Installer.exe          # Standalone version
├── AEPGP_ContextMenu-1.0.0.msi  # MSI version
├── USER_GUIDE.txt               # User documentation
├── README.txt                   # Quick start
└── SUPPORT.txt                  # Your contact info
```

**Create README.txt:**
```txt
AEPGP Context Menu Installer
=============================

Choose your installation method:

1. EASY INSTALL (Recommended for most users)
   - Double-click: AEPGP_Installer.exe
   - Click "Install"
   - Done!

2. PROFESSIONAL INSTALL (For IT departments)
   - Double-click: AEPGP_ContextMenu-1.0.0.msi
   - Follow the installation wizard

For detailed instructions, see USER_GUIDE.txt

Support: [Your contact information]
```

**Best for:**
- Giving users choice
- Mixed environments
- Professional distribution

## 🏗️ Build Process Comparison

| Feature | build_exe.bat | build_msi.bat |
|---------|---------------|---------------|
| Output | Single .exe | .msi installer |
| File size | 15-25 MB | 20-35 MB |
| Build time | 1-2 minutes | 2-4 minutes |
| Installation | Direct run | Wizard |
| Uninstall | Manual | Add/Remove Programs |
| Icon support | ✅ Yes | ✅ Yes |
| Version info | ✅ Yes | ✅ Yes |
| Code signing | ✅ Supported | ✅ Supported |
| Silent install | Custom | Built-in |

## 🔧 Full Customization Workflow

### Step-by-Step: Create Your Branded Installer

1. **Create Your Icon**
   ```cmd
   REM Place aepgp_icon.ico in windows_context_menu/
   ```

2. **Update Version Info**
   ```cmd
   notepad version_info.txt
   REM Update version, company, copyright
   ```

3. **Customize MSI (if building MSI)**
   ```cmd
   notepad create_msi.py
   REM Update APP_AUTHOR, APP_COMPANY, etc.
   ```

4. **Build Standalone EXE**
   ```cmd
   build_exe.bat
   ```

5. **Build MSI Installer**
   ```cmd
   build_msi.bat
   ```

6. **Test Both**
   ```cmd
   dist\AEPGP_Installer.exe
   dist\AEPGP_ContextMenu-1.0.0-win64.msi
   ```

7. **Create Distribution Package**
   ```cmd
   mkdir AEPGP_Package
   copy dist\AEPGP_Installer.exe AEPGP_Package\
   copy dist\*.msi AEPGP_Package\
   copy USER_GUIDE.txt AEPGP_Package\
   REM Add your README.txt and SUPPORT.txt
   ```

8. **Distribute!**

## 🧪 Testing Checklist

Before distributing:

### Standalone EXE Testing
- [ ] Runs without Python installed
- [ ] Icon appears correctly
- [ ] Version info visible (Right-click → Properties → Details)
- [ ] Install works
- [ ] Encryption works with AmbiSecure token
- [ ] Decryption works
- [ ] Only AmbiSecure tokens accepted (ATR check)
- [ ] Uninstall works
- [ ] Windows 10 compatible
- [ ] Windows 11 compatible
- [ ] No antivirus false positives

### MSI Testing
- [ ] Installation wizard works
- [ ] Appears in Add/Remove Programs
- [ ] Shortcuts created (if configured)
- [ ] Files in correct location
- [ ] Registry entries correct
- [ ] Uninstall removes everything
- [ ] Silent install works: `msiexec /i installer.msi /quiet`
- [ ] Upgrade from previous version works

## 📐 File Size Reference

| Package | Typical Size |
|---------|--------------|
| Source code only | ~200 KB |
| Standalone .exe | 15-25 MB |
| MSI installer | 20-35 MB |
| Complete package (both + docs) | 40-65 MB |

## 🔐 Code Signing (Optional but Recommended)

For production distribution:

### Get a Code Signing Certificate

**Option 1: Commercial CA**
- DigiCert, Sectigo, GlobalSign
- Cost: $100-500/year
- Trusted by Windows

**Option 2: Self-Signed (Testing Only)**
- Free
- Not trusted by Windows
- Shows security warnings

### Sign the EXE

```cmd
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist\AEPGP_Installer.exe
```

### Sign the MSI

```cmd
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com "dist\AEPGP_ContextMenu-1.0.0.msi"
```

### Benefits

- ✅ No security warnings
- ✅ Shows verified publisher
- ✅ Builds trust
- ✅ Required for some corporate environments

## 📞 Distribution Checklist

Before sending to users:

- [ ] Built latest version
- [ ] Tested on clean Windows 10 VM
- [ ] Tested on clean Windows 11 VM
- [ ] Updated USER_GUIDE.txt with your support info
- [ ] Created README.txt for the package
- [ ] Added SUPPORT.txt with contact information
- [ ] Virus scanned (Windows Defender + VirusTotal)
- [ ] File size is reasonable for your distribution method
- [ ] Named files clearly (include version number)
- [ ] Created checksums (SHA256) for verification
- [ ] Prepared release notes
- [ ] Code signed (if applicable)

## 🗂️ Version Control

Keep track of releases:

### Create CHANGELOG.txt

```txt
AEPGP Context Menu - Version History

Version 1.0.0 (2025-01-15)
--------------------------
- Initial release
- AmbiSecure token support (ATR: 3B D5 18 FF...)
- Encrypt/Decrypt context menu
- GUI installer
- Full AEPGP branding

Version 1.1.0 (Future)
--------------------------
- Bug fixes
- Performance improvements
- Updated dependencies
```

### Tag Releases

If using git:
```cmd
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## 🎯 Target Audience Recommendations

### For End Users (Non-Technical)
**Distribute:**
- Standalone .exe
- USER_GUIDE.txt
- Simple README.txt

**Why:** Easy, single-file, no wizard complexity

### For IT Departments
**Distribute:**
- MSI installer
- Technical documentation
- Silent install instructions
- Group Policy deployment guide

**Why:** Professional, deployable, manageable

### For Both
**Distribute:**
- Complete package with both
- Let them choose

**Why:** Flexibility

## 📈 Enterprise Deployment

### Silent Installation

**EXE:**
Custom implementation needed in your code

**MSI:**
```cmd
REM Silent install
msiexec /i AEPGP_ContextMenu-1.0.0.msi /quiet /norestart

REM With logging
msiexec /i AEPGP_ContextMenu-1.0.0.msi /quiet /norestart /l*v install.log

REM Silent uninstall
msiexec /x AEPGP_ContextMenu-1.0.0.msi /quiet /norestart
```

### Group Policy Deployment (MSI Only)

1. Place MSI on network share
2. Create new GPO
3. Computer Configuration → Software Installation
4. Add the MSI package
5. Link GPO to target OU
6. Computers auto-install on next restart

See [MSI_INSTALLER_GUIDE.md](MSI_INSTALLER_GUIDE.md) for details.

## 🔄 Update Workflow

When you make code changes:

1. **Update version number** in `version_info.txt` and `create_msi.py`
2. **Rebuild executables**
   ```cmd
   build_exe.bat
   build_msi.bat
   ```
3. **Test new versions**
4. **Create CHANGELOG entry**
5. **Distribute new versions**

MSI will automatically handle upgrades if version increases.

## 📚 Documentation Quick Reference

| Topic | File |
|-------|------|
| End users | USER_GUIDE.txt |
| Building executable | BUILD_INSTRUCTIONS.md |
| Building MSI | MSI_INSTALLER_GUIDE.md |
| Adding icon | CREATE_ICON.md |
| Updating version | UPDATE_VERSION.md |
| Distribution overview | DISTRIBUTION_README.md |
| Technical changes | AEPGP_CHANGES.md |
| **This complete guide** | **COMPLETE_BUILD_GUIDE.md** |

## 🎁 Summary

You now have everything needed for professional AEPGP distribution:

✅ **Standalone .exe** - Quick & easy
✅ **MSI installer** - Professional & enterprise-ready
✅ **Icon support** - Custom branding
✅ **Version information** - Professional metadata
✅ **User guide** - Complete documentation
✅ **Build scripts** - Automated building
✅ **Comprehensive docs** - Every detail covered

## 🚀 Ready to Distribute!

**Quick Commands:**

```cmd
REM Build everything
build_exe.bat
build_msi.bat

REM Your distributions are in:
dir dist\
```

Congratulations! Your AEPGP Context Menu is ready for professional distribution! 🎉
