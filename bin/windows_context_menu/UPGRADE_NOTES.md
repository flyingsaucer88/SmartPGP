# MSI Installer Upgrade Notes

## Automatic Upgrade Feature

The AEPGP Context Menu MSI installer now supports **automatic upgrades**. When you install a newer version, it will automatically uninstall the older version first.

## How It Works

### Upgrade Code
The MSI uses a persistent **Upgrade Code**: `{A1B2C3D4-E5F6-4A5B-8C9D-0E1F2A3B4C5D}`

This code:
- **Remains the same** across all versions
- Allows Windows Installer to detect previous installations
- Triggers automatic uninstallation of older versions before installing the new one

### Version Numbering

Current version: **1.0.1**

Version history:
- `1.0.0` - Initial release
- `1.0.1` - Added Gemalto card detection fix + automatic upgrade support

## Installation Behavior

### Installing Over an Older Version

When you run the new MSI installer (v1.0.1) on a system that has v1.0.0 installed:

1. Windows Installer detects the upgrade code match
2. Automatically uninstalls version 1.0.0
3. Installs version 1.0.1
4. **No user action required** - happens seamlessly

### Clean Installation

If no previous version is installed:
- Installs normally to `C:\Program Files\AEPGP Context Menu\`
- Creates Start Menu shortcut
- Registers context menu handlers

## For Developers

### Important Notes

⚠️ **NEVER CHANGE THE UPGRADE CODE** - This must remain constant across all versions for automatic upgrades to work.

### Building New Versions

1. Update `APP_VERSION` in `create_msi.py`
2. Keep `UPGRADE_CODE` unchanged
3. Build the MSI: `python create_msi.py bdist_msi`
4. Test upgrade on a system with the previous version installed

### Version Increment Guidelines

- **Major version** (x.0.0): Breaking changes, major feature additions
- **Minor version** (1.x.0): New features, enhancements, card support additions
- **Patch version** (1.0.x): Bug fixes, minor improvements

## Testing Upgrades

To test the upgrade process:

1. Install version 1.0.0 (old MSI)
2. Run version 1.0.1 (new MSI)
3. Verify:
   - Old version is automatically removed
   - New version installs successfully
   - Context menu still works
   - No duplicate entries in Add/Remove Programs

## Troubleshooting

### Upgrade Not Working?

If the automatic upgrade doesn't work:

1. Check Windows Event Viewer > Windows Logs > Application
2. Look for MSI installer errors
3. Manually uninstall old version via Control Panel
4. Install new version

### Finding Installed Version

Check in:
- Control Panel > Programs > Programs and Features
- Look for "AEPGP Context Menu"
- Version number is displayed

## Technical Details

### MSI Properties Used

```python
bdist_msi_options = {
    'upgrade_code': UPGRADE_CODE,     # Enables automatic upgrades
    'target_name': 'AEPGP_Context_Menu',  # Consistent internal name
}
```

### How Windows Installer Handles Upgrades

1. Detects matching upgrade code in registry
2. Executes **RemoveExistingProducts** action
3. Removes old installation
4. Proceeds with new installation
5. Updates registry with new version

---

**Last Updated:** 2025-12-30
**Current Version:** 1.0.1
