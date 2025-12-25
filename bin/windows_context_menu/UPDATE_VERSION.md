# Updating Version Information

## What is Version Information?

Version information is metadata embedded in the Windows executable that shows:
- Product name and version
- Company name
- File description
- Copyright information
- Internal version numbers

Users can see this by right-clicking the `.exe` → Properties → Details tab.

## Current Version

**File:** `version_info.txt`

```
Product Name: AEPGP Context Menu
Version: 1.0.0.0
Company: AEPGP
Description: AEPGP Context Menu Installer
```

## How to Update Version

### For a New Release (e.g., 1.0 → 1.1)

1. Open `version_info.txt` in a text editor

2. Find these lines and update the version numbers:

```python
filevers=(1, 0, 0, 0),     # Change to (1, 1, 0, 0)
prodvers=(1, 0, 0, 0),     # Change to (1, 1, 0, 0)
```

And:

```python
StringStruct(u'FileVersion', u'1.0.0.0'),      # Change to '1.1.0.0'
StringStruct(u'ProductVersion', u'1.0.0.0')    # Change to '1.1.0.0'
```

3. Save the file

4. Rebuild the executable:
```cmd
build_exe.bat
```

5. The new executable will have updated version info

## Version Number Format

Format: `MAJOR.MINOR.PATCH.BUILD`

Examples:
- `1.0.0.0` - Initial release
- `1.1.0.0` - Minor update (new features)
- `1.0.1.0` - Patch (bug fixes)
- `1.0.0.1` - Build number increment

### When to Increment:

- **MAJOR (1.x.x.x):** Major changes, breaking changes
- **MINOR (x.1.x.x):** New features, significant updates
- **PATCH (x.x.1.x):** Bug fixes, minor improvements
- **BUILD (x.x.x.1):** Internal builds, daily builds

## Customizing Company Name

Change this line:

```python
StringStruct(u'CompanyName', u'AEPGP'),
```

To:

```python
StringStruct(u'CompanyName', u'Your Company Name'),
```

## Customizing Description

Change this line:

```python
StringStruct(u'FileDescription', u'AEPGP Context Menu Installer'),
```

To your preferred description.

## Customizing Copyright

Change this line:

```python
StringStruct(u'LegalCopyright', u'Based on SmartPGP (GPL v2) by ANSSI'),
```

Example:

```python
StringStruct(u'LegalCopyright', u'Copyright (C) 2025 Your Company. GPL v2'),
```

## Example: Full Version Update

Let's say you're releasing version 2.0:

**Before:**
```python
filevers=(1, 0, 0, 0),
prodvers=(1, 0, 0, 0),
...
StringStruct(u'FileVersion', u'1.0.0.0'),
StringStruct(u'ProductVersion', u'1.0.0.0')
```

**After:**
```python
filevers=(2, 0, 0, 0),
prodvers=(2, 0, 0, 0),
...
StringStruct(u'FileVersion', u'2.0.0.0'),
StringStruct(u'ProductVersion', u'2.0.0.0')
```

Then rebuild:
```cmd
build_exe.bat
```

## Viewing Version Info

After building with version info:

**Method 1: File Properties**
1. Navigate to `dist/`
2. Right-click `AEPGP_Installer.exe`
3. Select "Properties"
4. Click "Details" tab
5. See all version information

**Method 2: PowerShell**
```powershell
(Get-Item .\dist\AEPGP_Installer.exe).VersionInfo
```

**Method 3: Command Line**
```cmd
wmic datafile where name="C:\\path\\to\\AEPGP_Installer.exe" get Version
```

## Complete version_info.txt Template

```python
VSVersionInfo(
  ffi=FixedFileInfo(
    # File version (MAJOR, MINOR, PATCH, BUILD)
    filevers=(1, 0, 0, 0),
    # Product version (MAJOR, MINOR, PATCH, BUILD)
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,    # Windows NT
    fileType=0x1,  # Application
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',  # Language: English (US), Charset: Unicode
        [
        # Company/Organization Name
        StringStruct(u'CompanyName', u'Your Company'),

        # Short description of what the file does
        StringStruct(u'FileDescription', u'AEPGP Context Menu Installer'),

        # File version as string
        StringStruct(u'FileVersion', u'1.0.0.0'),

        # Internal name (usually filename without extension)
        StringStruct(u'InternalName', u'AEPGP_Installer'),

        # Copyright notice
        StringStruct(u'LegalCopyright', u'Copyright (C) 2025 Your Company'),

        # Original filename
        StringStruct(u'OriginalFilename', u'AEPGP_Installer.exe'),

        # Product name
        StringStruct(u'ProductName', u'AEPGP Context Menu'),

        # Product version as string
        StringStruct(u'ProductVersion', u'1.0.0.0')
        ])
      ]),
    # Translation info: 1033 = English (US), 1200 = Unicode
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
```

## Language Codes

If you want to change the language:

| Language | Code |
|----------|------|
| English (US) | 1033 |
| English (UK) | 2057 |
| French | 1036 |
| German | 1031 |
| Spanish | 1034 |
| Italian | 1040 |
| Japanese | 1041 |

Change this line:
```python
StringTable(u'040904B0',  # 0409 = English (US), 04B0 = Unicode
```

## Common Issues

### Issue: Version info doesn't appear
**Solution:**
- Make sure `version_info.txt` exists
- Check for syntax errors in the file
- Rebuild completely: delete `build/` and `dist/`, then rebuild

### Issue: Wrong encoding
**Solution:**
- File must be UTF-8 encoded
- Keep the `# UTF-8` comment at the top

### Issue: Build fails with version_info.txt
**Solution:**
- Check for typos in the file
- Ensure all parentheses and brackets match
- Don't add extra fields not shown in the template

## Best Practices

1. **Always increment version** for each release
2. **Use semantic versioning** (MAJOR.MINOR.PATCH)
3. **Update copyright year** when building new releases
4. **Keep FileVersion and ProductVersion in sync**
5. **Document version changes** in a CHANGELOG file

## Automation

For automated builds, you can generate `version_info.txt` dynamically:

```python
# generate_version.py
import datetime

version = "1.0.0.0"
year = datetime.datetime.now().year

template = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version.replace('.', ', ')}),
    prodvers=({version.replace('.', ', ')}),
    ...
  ),
  kids=[
    StringFileInfo([
      StringTable(u'040904B0', [
        StringStruct(u'FileVersion', u'{version}'),
        StringStruct(u'LegalCopyright', u'Copyright (C) {year} Your Company'),
        ...
      ])
    ]),
    ...
  ]
)
"""

with open('version_info.txt', 'w', encoding='utf-8') as f:
    f.write(template)
```

Then run before building:
```cmd
python generate_version.py
build_exe.bat
```

## Version History Example

Keep track of versions in a CHANGELOG file:

```
# AEPGP Context Menu - Version History

## Version 1.0.0 (2025-01-01)
- Initial release
- AmbiSecure token support
- Encrypt/Decrypt context menu
- GUI installer

## Version 1.1.0 (2025-02-01)
- Added support for additional file formats
- Improved error messages
- Performance optimizations

## Version 1.1.1 (2025-02-15)
- Fixed bug with Windows 11 context menu
- Updated documentation
```

## Quick Reference

| What to Update | Where |
|----------------|-------|
| Version number | `filevers` and `prodvers` tuples |
| Version string | `FileVersion` and `ProductVersion` strings |
| Company name | `CompanyName` string |
| Description | `FileDescription` string |
| Copyright | `LegalCopyright` string |

After any change: **Rebuild with `build_exe.bat`**
