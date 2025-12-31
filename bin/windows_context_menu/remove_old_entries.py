"""
Remove Old AEPGP Menu Entries Only

This script removes ONLY the old menu entries (like AEPGP.Encrypt)
while keeping the new cascading AEPGP menu intact.
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


def main():
    """Remove old AEPGP menu entries"""
    print("=" * 70)
    print("Remove Old AEPGP Menu Entries")
    print("=" * 70)

    if sys.platform != 'win32':
        print("\nERROR: This script is only for Windows operating systems.")
        print("Press Enter to exit...")
        input()
        sys.exit(1)

    if not is_admin():
        print("\nThis script requires Administrator privileges.")
        print("Requesting elevation...")
        if elevate_privileges():
            sys.exit(0)
        else:
            print("\nERROR: Could not obtain Administrator privileges.")
            print("Please run this script as Administrator.")
            print("\nPress Enter to exit...")
            input()
            sys.exit(1)

    print("\nRunning with Administrator privileges...")
    print("\nRemoving old AEPGP menu entries (keeping new cascading menu)...")
    print()

    # Old keys to remove
    old_keys = [
        r"*\shell\AEPGP.Encrypt",
        r"*\shell\EncryptWithAEPGP",
        r"*\shell\AEPGP_Encrypt",
        r"*\shell\Encrypt with AEPGP",
    ]

    removed_count = 0
    for old_key in old_keys:
        if delete_registry_key(winreg.HKEY_CLASSES_ROOT, old_key):
            print(f"[OK] Removed: {old_key}")
            removed_count += 1

    print()
    print("=" * 70)
    if removed_count > 0:
        print(f"Removed {removed_count} old menu entr{'y' if removed_count == 1 else 'ies'}.")
        print()
        print("The new AEPGP cascading menu has been preserved.")
        print()
        print("IMPORTANT: Restart Windows Explorer for changes to take effect:")
        print("  1. Press Ctrl+Shift+Esc (Task Manager)")
        print("  2. Find 'Windows Explorer'")
        print("  3. Right-click -> Restart")
    else:
        print("No old menu entries found.")
        print()
        print("The new AEPGP cascading menu should be visible.")
        print("If you don't see it, try restarting Windows Explorer.")

    print()
    print("=" * 70)
    print("\nPress Enter to exit...")
    input()


if __name__ == "__main__":
    main()
