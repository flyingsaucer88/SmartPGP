"""
AEPGP Windows Context Menu Uninstaller

This script removes the Windows Explorer context menu entries for AEPGP.

IMPORTANT: This script requires Administrator privileges to modify the Windows
registry (HKEY_CLASSES_ROOT).
"""

import sys
import os
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
        # Re-run the script with elevation
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",  # Request elevation
            sys.executable,  # Python interpreter
            " ".join([f'"{arg}"' for arg in sys.argv]),  # Script and arguments
            None,
            1  # SW_SHOWNORMAL
        )
        return True
    except Exception as e:
        print(f"ERROR: Failed to elevate privileges: {e}")
        return False


def delete_registry_key(key_path):
    """
    Recursively delete a registry key and all its subkeys.

    Args:
        key_path: Registry key path relative to HKEY_CLASSES_ROOT

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Open the key
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, key_path, 0, winreg.KEY_ALL_ACCESS)

        # Enumerate and delete all subkeys first
        subkeys = []
        i = 0
        while True:
            try:
                subkey_name = winreg.EnumKey(key, i)
                subkeys.append(subkey_name)
                i += 1
            except OSError:
                break

        # Delete subkeys recursively
        for subkey_name in subkeys:
            delete_registry_key(key_path + "\\" + subkey_name)

        winreg.CloseKey(key)

        # Delete the key itself
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, key_path)
        return True

    except FileNotFoundError:
        # Key doesn't exist, that's okay
        return True
    except Exception as e:
        print(f"Error deleting key {key_path}: {e}")
        return False


def uninstall_encrypt_menu():
    """Remove the 'Encrypt with AEPGP' context menu item"""
    try:
        key_path = r"*\shell\AEPGP.Encrypt"
        if delete_registry_key(key_path):
            print("✓ Removed 'Encrypt with AEPGP' menu item")
            return True
        else:
            print("✗ Failed to remove 'Encrypt with AEPGP' menu item")
            return False
    except Exception as e:
        print(f"✗ Error removing encrypt menu: {e}")
        return False


def uninstall_decrypt_menu():
    """Remove the 'Decrypt with AEPGP' context menu items"""
    try:
        extensions = [".gpg", ".pgp", ".asc"]
        success_count = 0

        for ext in extensions:
            try:
                key_path = f"{ext}\\shell\\AEPGP.Decrypt"
                if delete_registry_key(key_path):
                    print(f"✓ Removed 'Decrypt with AEPGP' for {ext} files")
                    success_count += 1
                else:
                    print(f"✗ Failed to remove 'Decrypt with AEPGP' for {ext} files")
            except Exception as e:
                print(f"✗ Error removing decrypt menu for {ext}: {e}")

        return success_count > 0

    except Exception as e:
        print(f"✗ Error removing decrypt menu: {e}")
        return False


def verify_uninstallation():
    """Verify that the context menu entries were removed"""
    try:
        # Check if encrypt menu still exists
        try:
            key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\AEPGP.Encrypt")
            winreg.CloseKey(key)
            print("\nWarning: Encrypt menu still exists in registry")
            return False
        except FileNotFoundError:
            print("\n✓ Encrypt menu successfully removed")

        # Check if decrypt menu still exists
        try:
            key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r".gpg\shell\AEPGP.Decrypt")
            winreg.CloseKey(key)
            print("Warning: Decrypt menu still exists in registry")
            return False
        except FileNotFoundError:
            print("✓ Decrypt menu successfully removed")

        return True
    except Exception as e:
        print(f"\nWarning: Could not verify uninstallation: {e}")
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
            sys.exit(0)  # Exit this instance, elevated instance will run
        else:
            print("\nERROR: Could not obtain Administrator privileges.")
            print("Please run this script as Administrator.")
            print("\nPress Enter to exit...")
            input()
            sys.exit(1)

    print("\nRunning with Administrator privileges ✓")

    # Confirm uninstallation
    print("\nThis will remove AEPGP context menu items from Windows Explorer.")
    response = input("Do you want to continue? (yes/no): ")

    if response.lower() not in ['yes', 'y']:
        print("\nUninstallation cancelled.")
        print("Press Enter to exit...")
        input()
        sys.exit(0)

    # Uninstall menu items
    print("\n" + "=" * 70)
    print("Removing context menu items...")
    print("=" * 70)

    encrypt_ok = uninstall_encrypt_menu()
    decrypt_ok = uninstall_decrypt_menu()

    # Verify uninstallation
    print("\n" + "=" * 70)
    print("Verifying uninstallation...")
    print("=" * 70)
    verify_uninstallation()

    # Summary
    print("\n" + "=" * 70)
    if encrypt_ok or decrypt_ok:
        print("Uninstallation completed successfully! ✓")
        print("\nAEPGP context menu items have been removed.")
    else:
        print("No AEPGP context menu items were found.")

    print("\nPress Enter to exit...")
    input()


if __name__ == "__main__":
    main()
