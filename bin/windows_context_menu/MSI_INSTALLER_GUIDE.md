# Creating an MSI Installer Package

## What is an MSI Installer?

MSI (Microsoft Installer) is the professional standard for Windows software installation. Compared to a standalone .exe:

### Advantages of MSI:
✅ **Professional appearance** - Standard Windows installer experience
✅ **Add/Remove Programs** - Appears in Windows Settings → Apps
✅ **Group Policy deployment** - Can be deployed via Active Directory
✅ **Repair functionality** - Built-in repair option
✅ **Uninstall tracking** - Clean uninstallation
✅ **Corporate friendly** - IT departments prefer MSI files
✅ **Silent installation** - Can install without user interaction: `msiexec /i installer.msi /quiet`

### Disadvantages:
❌ **Larger file size** - Usually bigger than standalone .exe
❌ **More complex** - Requires additional tools
❌ **Slower to create** - Build process takes longer

## Two Approaches

### Approach 1: cx_Freeze (Easier, Recommended)

**Pros:**
- Pure Python solution
- Creates both .exe and .msi
- No additional tools needed
- Easy to configure

**Cons:**
- Less control over installer appearance
- Larger file size

### Approach 2: WiX Toolset (Advanced)

**Pros:**
- Professional-grade MSI creation
- Full control over installation process
- Smaller file size
- Custom UI possible

**Cons:**
- Requires learning WiX XML
- Separate tool installation needed
- More complex setup

## Quick Start (cx_Freeze Method)

### Prerequisites

```cmd
pip install cx_Freeze pyscard
```

### Build the MSI

```cmd
build_msi.bat
```

### Output

```
dist/
└── AEPGP Context Menu-1.0.0-win64.msi
```

## Detailed cx_Freeze Guide

### Step 1: Install cx_Freeze

```cmd
pip install cx_Freeze
```

### Step 2: Run the Build Script

```cmd
python create_msi.py bdist_msi
```

Or use the batch file:

```cmd
build_msi.bat
```

### Step 3: Find Your MSI

The MSI file will be in:
```
dist/AEPGP Context Menu-1.0.0-win64.msi
```

## MSI Configuration

Edit `create_msi.py` to customize:

### Change Version

```python
APP_VERSION = "1.0.0"  # Change this
```

### Change Install Location

```python
bdist_msi_options = {
    'initial_target_dir': r'[ProgramFilesFolder]\Your Folder Name',
    ...
}
```

Common install locations:
- `[ProgramFilesFolder]` - C:\Program Files\
- `[ProgramFiles64Folder]` - C:\Program Files\
- `[CommonAppDataFolder]` - C:\ProgramData\
- `[LocalAppDataFolder]` - C:\Users\{user}\AppData\Local\

### Add Desktop Shortcut

```python
exe = Executable(
    ...
    shortcut_name='AEPGP Installer',
    shortcut_dir='DesktopFolder',  # Creates desktop shortcut
)
```

### Add Start Menu Shortcut

```python
exe = Executable(
    ...
    shortcut_name='AEPGP Installer',
    shortcut_dir='ProgramMenuFolder',  # Start menu
)
```

## Using WiX Toolset (Advanced)

If you need more control, use WiX Toolset:

### Step 1: Install WiX

1. Download from: https://wixtoolset.org/
2. Install WiX Toolset 3.11 or later
3. Add to PATH

### Step 2: Create WiX Configuration

Create `aepgp_installer.wxs`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*"
           Name="AEPGP Context Menu"
           Language="1033"
           Version="1.0.0.0"
           Manufacturer="AEPGP"
           UpgradeCode="PUT-GUID-HERE">

    <Package InstallerVersion="200" Compressed="yes" InstallScope="perMachine" />

    <MajorUpgrade DowngradeErrorMessage="A newer version is already installed." />
    <MediaTemplate EmbedCab="yes" />

    <Feature Id="ProductFeature" Title="AEPGP Context Menu" Level="1">
      <ComponentGroupRef Id="ProductComponents" />
    </Feature>
  </Product>

  <Fragment>
    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFilesFolder">
        <Directory Id="INSTALLFOLDER" Name="AEPGP Context Menu" />
      </Directory>
    </Directory>
  </Fragment>

  <Fragment>
    <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
      <Component Id="MainExecutable" Guid="PUT-GUID-HERE">
        <File Source="dist\AEPGP_Installer.exe" KeyPath="yes" />
      </Component>
    </ComponentGroup>
  </Fragment>
</Wix>
```

### Step 3: Generate GUIDs

```cmd
python -c "import uuid; print(uuid.uuid4())"
```

### Step 4: Compile WiX

```cmd
candle aepgp_installer.wxs
light aepgp_installer.wixobj
```

This creates `aepgp_installer.msi`

## Testing the MSI

### Test Installation

1. **Double-click the .msi file**
2. Follow the installation wizard
3. Click "Install"
4. Check that files are in the install directory
5. Check Start Menu for shortcuts

### Test Uninstallation

1. **Windows Settings → Apps**
2. Find "AEPGP Context Menu"
3. Click "Uninstall"
4. Verify files are removed
5. Verify registry entries are cleaned

### Test Silent Installation

```cmd
msiexec /i "AEPGP Context Menu-1.0.0-win64.msi" /quiet /norestart
```

### Test Silent Uninstallation

```cmd
msiexec /x "AEPGP Context Menu-1.0.0-win64.msi" /quiet /norestart
```

### Test Logging

```cmd
msiexec /i "AEPGP Context Menu-1.0.0-win64.msi" /l*v install.log
```

Check `install.log` for any errors.

## MSI vs EXE Comparison

| Feature | Standalone EXE | MSI Installer |
|---------|----------------|---------------|
| File size | Smaller (~15-25 MB) | Larger (~20-35 MB) |
| Build time | Faster | Slower |
| User experience | Custom GUI | Standard Windows wizard |
| Add/Remove Programs | No | Yes |
| Group Policy deployment | No | Yes |
| Silent install | Custom implementation | Built-in |
| Repair option | No | Yes |
| IT department friendly | Less | More |

## When to Use Each

### Use Standalone EXE When:
- Quick distribution needed
- Small-scale deployment
- Users are tech-savvy
- File size matters
- Custom installation flow needed

### Use MSI When:
- Corporate/enterprise environment
- Group Policy deployment
- Professional appearance required
- IT department is involved
- Need Add/Remove Programs entry
- Silent installation required

## Distribution

### MSI File Naming

Good naming convention:
```
ProductName-Version-Architecture.msi
```

Examples:
```
AEPGP_ContextMenu-1.0.0-win64.msi
AEPGP_ContextMenu-1.1.0-x64.msi
```

### What to Distribute

**Option 1: MSI Only**
```
AEPGP_ContextMenu-1.0.0-win64.msi
```

**Option 2: Complete Package**
```
AEPGP_Package/
├── AEPGP_ContextMenu-1.0.0-win64.msi
├── README.txt
├── INSTALL_INSTRUCTIONS.txt
└── SUPPORT.txt
```

## Group Policy Deployment

For enterprise environments:

### Step 1: Share MSI on Network

Place MSI on a network share:
```
\\server\software\AEPGP_ContextMenu-1.0.0.msi
```

### Step 2: Create GPO

1. Open Group Policy Management
2. Create new GPO
3. Edit GPO
4. Navigate to: Computer Configuration → Policies → Software Settings → Software Installation
5. Right-click → New → Package
6. Select the MSI file
7. Choose "Assigned"

### Step 3: Link to OU

Link the GPO to the appropriate Organizational Unit.

Computers will automatically install AEPGP on next restart.

## Troubleshooting

### Build Fails

**Error: "cx_Freeze not found"**
```cmd
pip install cx_Freeze
```

**Error: "Module not found"**
Add to `packages` list in `create_msi.py`

### Installation Fails

**Error: "Another version is installed"**
- Uninstall the old version first
- Or increment version number

**Error: "Insufficient privileges"**
- Run as Administrator
- Or use elevated command prompt

### MSI Won't Uninstall

1. Open Registry Editor
2. Navigate to: `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall`
3. Find AEPGP entry
4. Note the UninstallString
5. Run that command manually

## Advanced Features

### Add License Agreement

Edit `create_msi.py`:

```python
bdist_msi_options = {
    ...
    'license_file': 'LICENSE.txt',  # Add license file
}
```

### Custom Install Icon

```python
bdist_msi_options = {
    ...
    'install_icon': 'aepgp_icon.ico',
}
```

### Upgrade Handling

MSI automatically handles upgrades if version numbers increase.

## File Size Optimization

MSI files are larger because they include:
- All files in compressed cabinet (.cab)
- Installation database
- UI resources
- Registry settings

Typical sizes:
- Standalone .exe: 15-25 MB
- cx_Freeze MSI: 20-35 MB
- WiX MSI: 18-30 MB

## Best Practices

1. ✅ **Test on clean VM** before distribution
2. ✅ **Use semantic versioning** (1.0.0)
3. ✅ **Include all dependencies**
4. ✅ **Test silent installation**
5. ✅ **Provide uninstall option**
6. ✅ **Sign the MSI** (for production)
7. ✅ **Document installation process**
8. ✅ **Test on Windows 10 and 11**

## Code Signing MSI

For production:

```cmd
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com "AEPGP_ContextMenu-1.0.0.msi"
```

Benefits:
- Trusted publisher
- No security warnings
- Corporate policy compliance

## Quick Reference

| Task | Command |
|------|---------|
| Build MSI | `build_msi.bat` |
| Install | Double-click .msi |
| Silent install | `msiexec /i installer.msi /quiet` |
| Uninstall | Windows Settings → Apps |
| Silent uninstall | `msiexec /x installer.msi /quiet` |
| Install with log | `msiexec /i installer.msi /l*v log.txt` |

## Summary

**For most users:** Use the standalone .exe (simpler, smaller)
**For enterprise:** Use the MSI installer (professional, deployable)
**For both:** Build both and let users choose!

To build both:
```cmd
REM Build standalone exe
build_exe.bat

REM Build MSI installer
build_msi.bat

REM Now you have both in dist/
```

Distribute whichever format suits your users best!
