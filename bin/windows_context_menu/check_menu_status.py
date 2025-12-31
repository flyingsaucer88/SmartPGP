"""
AEPGP Context Menu Status Checker

This script checks the current state of AEPGP context menu entries
and provides instructions for fixing any issues.
"""

import winreg
import sys
import io

# Fix Unicode output for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def check_key_exists(root, path):
    """Check if a registry key exists."""
    try:
        key = winreg.OpenKey(root, path)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Error checking {path}: {e}")
        return False

def get_subkeys(root, path):
    """Get list of subkey names under a registry key."""
    try:
        key = winreg.OpenKey(root, path)
        subkeys = []
        i = 0
        while True:
            try:
                subkey_name = winreg.EnumKey(key, i)
                subkeys.append(subkey_name)
                i += 1
            except OSError:
                break
        winreg.CloseKey(key)
        return subkeys
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error reading subkeys from {path}: {e}")
        return []

print("=" * 70)
print("AEPGP Context Menu Status Checker")
print("=" * 70)
print()

# Check for new cascading menu structure
new_menu_exists = check_key_exists(winreg.HKEY_CLASSES_ROOT, r"*\shell\AEPGP")
new_desktop_menu_exists = check_key_exists(winreg.HKEY_CLASSES_ROOT, r"Directory\Background\shell\AEPGP")

# Check for old menu entries (common old key names)
old_keys_to_check = [
    r"*\shell\EncryptWithAEPGP",
    r"*\shell\AEPGP_Encrypt",
    r"*\shell\Encrypt with AEPGP",
]

old_menu_entries = []
for key_path in old_keys_to_check:
    if check_key_exists(winreg.HKEY_CLASSES_ROOT, key_path):
        old_menu_entries.append(key_path)

# Check all shell entries for AEPGP-related keys
all_shell_keys = get_subkeys(winreg.HKEY_CLASSES_ROOT, r"*\shell")
aepgp_related_keys = [k for k in all_shell_keys if 'aepgp' in k.lower() or 'encrypt' in k.lower()]

print("Current Status:")
print("-" * 70)
print()

if new_menu_exists:
    print("[OK] NEW cascading menu structure: FOUND")
    print("  Location: HKEY_CLASSES_ROOT\\*\\shell\\AEPGP")

    # Check submenu items
    submenu_items = get_subkeys(winreg.HKEY_CLASSES_ROOT, r"*\shell\AEPGP\shell")
    if submenu_items:
        print(f"  Submenu items found ({len(submenu_items)}):")
        for item in submenu_items:
            print(f"    - {item}")
else:
    print("[FAIL] NEW cascading menu structure: NOT FOUND")
    print("  Expected location: HKEY_CLASSES_ROOT\\*\\shell\\AEPGP")

print()

if new_desktop_menu_exists:
    print("[OK] Desktop background menu: FOUND")
    print("  Location: HKEY_CLASSES_ROOT\\Directory\\Background\\shell\\AEPGP")
else:
    print("[FAIL] Desktop background menu: NOT FOUND")

print()

if old_menu_entries:
    print("[WARN] OLD menu entries found (should be removed):")
    for entry in old_menu_entries:
        print(f"  - {entry}")
else:
    print("[OK] No known old menu entries found")

print()

if aepgp_related_keys:
    print(f"All AEPGP/encrypt-related keys in *\\shell ({len(aepgp_related_keys)}):")
    for key in aepgp_related_keys:
        print(f"  - {key}")
else:
    print("No AEPGP-related keys found in *\\shell")

print()
print("=" * 70)
print("Diagnosis:")
print("=" * 70)
print()

if new_menu_exists and not old_menu_entries:
    print("[OK] Everything looks good!")
    print("  The new cascading menu is installed and no old entries detected.")
    print()
    print("  You should see: Right-click file -> AEPGP -> submenu items")
    print()
    print("  NOTE: On Windows 11, you may need to click 'Show more options'")
    print("        or use SHIFT+Right-click to see the menu.")

elif not new_menu_exists and not old_menu_entries:
    print("[FAIL] No AEPGP menu installed (neither old nor new)")
    print()
    print("  ACTION REQUIRED: Run INSTALL.bat to install the menu")

elif new_menu_exists and old_menu_entries:
    print("[WARN] Both old and new menu entries exist!")
    print()
    print("  This can cause conflicts. The old entries may appear instead of new.")
    print()
    print("  ACTION REQUIRED: Run REINSTALL.bat to clean up old entries")

else:  # old exists but new doesn't
    print("[WARN] Only old menu entries found")
    print()
    print("  You're seeing the old menu structure, not the new cascading menu.")
    print()
    print("  ACTION REQUIRED: Run REINSTALL.bat to upgrade to cascading menu")

print()
print("=" * 70)
print()
print("Press Enter to exit...")
input()
