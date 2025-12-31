"""
AEPGP Windows Context Menu Uninstaller - Cascading Menu Version

This script removes the AEPGP cascading context menu entries.

IMPORTANT: This script requires Administrator privileges.
"""

import sys
import winreg
import ctypes


def is_admin():
    """Check if the script is running with Administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def elevate_privileges():
    """Re-run the script with Administrator privileges"""
    if sys.platform != 'win32':
        print("ERROR: This script is only for Windows")
        return False

    try:
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            " ".join([f'"{arg}"' for arg in sys.argv]),
            None,
            1
        )
        return True
    except Exception as e:
        print(f"ERROR: Failed to elevate privileges: {e}")
        return False


def delete_registry_key(root_key, key_path):
    """Recursively delete a registry key and all its subkeys"""
    try:
        # Open the key
        key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_ALL_ACCESS)

        # Get all subkeys
        subkeys = []
        try:
            i = 0
            while True:
                subkey_name = winreg.EnumKey(key, i)
                subkeys.append(subkey_name)
                i += 1
        except WindowsError:
            pass

        # Recursively delete subkeys
        for subkey_name in subkeys:
            delete_registry_key(root_key, f"{key_path}\\{subkey_name}")

        # Close and delete the key
        winreg.CloseKey(key)
        winreg.DeleteKey(root_key, key_path)
        return True

    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Warning: Could not delete {key_path}: {e}")
        return False


def uninstall_cascading_menus():
    """Remove all AEPGP cascading context menu entries"""
    success_count = 0

    print("\nRemoving AEPGP context menu entries...")

    # Remove AEPGP menu for all files
    if delete_registry_key(winreg.HKEY_CLASSES_ROOT, r"*\shell\AEPGP"):
        print("  ✓ Removed AEPGP menu from files")
        success_count += 1
    else:
        print("  ⚠ AEPGP file menu not found (may not be installed)")

    # Remove AEPGP menu from desktop background
    if delete_registry_key(winreg.HKEY_CLASSES_ROOT, r"Directory\Background\shell\AEPGP"):
        print("  ✓ Removed AEPGP menu from desktop")
        success_count += 1
    else:
        print("  ⚠ AEPGP desktop menu not found (may not be installed)")

    # Remove old and current flat menu entries
    old_keys = [
        r"*\shell\AEPGP.Encrypt",
        r"*\shell\EncryptWithAEPGP",
        r"*\shell\AEPGP_Encrypt",
        r"*\shell\AEPGP_Decrypt",
        r"*\shell\AEPGP_GenerateKeys",
        r"*\shell\AEPGP_DeleteKeys",
        r"*\shell\AEPGP_ChangePIN",
        r"*\shell\AEPGP_ImportPFX",
        r"*\shell\Encrypt with AEPGP",
        r".pfx\shell\AEPGP_ImportPFX",
        r".p12\shell\AEPGP_ImportPFX",
    ]

    for old_key in old_keys:
        if delete_registry_key(winreg.HKEY_CLASSES_ROOT, old_key):
            print(f"  ✓ Removed entry: {old_key}")
            success_count += 1

    return success_count > 0


def remove_version_info():
    """Remove version information from registry"""
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\AEPGP\ContextMenu")
        print("  ✓ Removed version information")
        return True
    except FileNotFoundError:
        return True  # Already doesn't exist
    except Exception as e:
        print(f"  ⚠ Could not remove version info: {e}")
        return False


def main():
    """Main uninstallation function"""
    print("=" * 70)
    print("AEPGP Windows Context Menu Uninstaller")
    print("=" * 70)

    # Check if running on Windows
    if sys.platform != 'win32':
        print("\nERROR: This uninstaller is only for Windows operating systems.")
        print("Press Enter to exit...")
        input()
        sys.exit(1)

    # Check for admin privileges
    if not is_admin():
        print("\nThis uninstaller requires Administrator privileges.")
        print("Requesting elevation...")
        if elevate_privileges():
            sys.exit(0)
        else:
            print("\nERROR: Could not obtain Administrator privileges.")
            print("Please run this script as Administrator.")
            print("\nPress Enter to exit...")
            input()
            sys.exit(1)

    print("\nRunning with Administrator privileges ✓")

    # Confirm uninstallation (unless --silent flag)
    if "--silent" not in sys.argv:
        print("\nThis will remove all AEPGP context menu entries.")
        response = input("Continue with uninstallation? (yes/no): ")

        if response.lower() not in ['yes', 'y']:
            print("\nUninstallation cancelled.")
            print("Press Enter to exit...")
            input()
            sys.exit(0)

    # Perform uninstallation
    print("\n" + "=" * 70)
    print("Uninstalling AEPGP context menu...")
    print("=" * 70)

    menu_removed = uninstall_cascading_menus()
    version_removed = remove_version_info()

    # Summary
    print("\n" + "=" * 70)
    if menu_removed:
        print("Uninstallation completed successfully! ✓")
        print("\nAEPGP context menu entries have been removed.")
        print("You may need to restart Windows Explorer for changes to take effect.")
        print("\nTo restart Explorer:")
        print("  1. Press Ctrl+Shift+Esc (Task Manager)")
        print("  2. Find 'Windows Explorer'")
        print("  3. Right-click → Restart")
    else:
        print("No AEPGP context menu entries found.")
        print("AEPGP may not be installed or was already uninstalled.")

    if not "--silent" in sys.argv:
        print("\nPress Enter to exit...")
        input()


if __name__ == "__main__":
    main()
