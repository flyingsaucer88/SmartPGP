"""
AEPGP Windows Context Menu Uninstaller - Cascading Menu Version

This script removes the AEPGP cascading context menu entries.

IMPORTANT: This script requires Administrator privileges.
"""

import sys
import os
import glob
import subprocess
import winreg
import ctypes

# CLSID of the COM shell extension — must match AEPGPContextMenu.cs exactly
SHELL_EXT_CLSID = "{3F7E8D9A-B1C2-4E5F-8A6B-9C0D1E2F3A4B}"


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


def _find_dotnet_tool(tool_name, prefer_x64=True):
    """Locate a .NET Framework 4.x tool (RegAsm.exe).  Same logic as install_menu.py."""
    roots = (
        [r"C:\Windows\Microsoft.NET\Framework64",
         r"C:\Windows\Microsoft.NET\Framework"]
        if prefer_x64
        else [r"C:\Windows\Microsoft.NET\Framework",
              r"C:\Windows\Microsoft.NET\Framework64"]
    )
    for root in roots:
        preferred = os.path.join(root, "v4.0.30319", tool_name)
        if os.path.isfile(preferred):
            return preferred
        for p in sorted(glob.glob(os.path.join(root, "v4*", tool_name)), reverse=True):
            if os.path.isfile(p):
                return p
    return None


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


def uninstall_com_shell_ext():
    """Unregister and remove the COM shell extension.

    Steps:
      1. Read DllPath from HKLM\\SOFTWARE\\AEPGP\\ContextMenu (written by installer).
      2. If the DLL file exists, run RegAsm /unregister to call [ComUnregisterFunction],
         which removes the shellex handler keys written at registration time.
      3. As a belt-and-suspenders fallback, also directly delete the shellex and
         CLSID keys — covers the case where the DLL has already been deleted.
      4. Remove HKLM\\SOFTWARE\\AEPGP\\ContextMenu (installer-written paths).

    Returns True if anything was removed; False if the extension was not installed.
    """
    removed_anything = False

    # ── Step 1: read DLL path from registry ──────────────────────────────
    dll_path = None
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"SOFTWARE\AEPGP\ContextMenu") as k:
            dll_path = winreg.QueryValueEx(k, "DllPath")[0]
    except FileNotFoundError:
        pass  # Key absent — extension was never installed or already removed
    except Exception as e:
        print(f"  ⚠ Could not read DllPath from registry: {e}")

    # Fall back to path relative to this script
    if not dll_path:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dll_path = os.path.join(script_dir, "com_shell_ext", "AEPGPContextMenu.dll")

    # ── Step 2: RegAsm /unregister (calls [ComUnregisterFunction]) ────────
    if os.path.isfile(dll_path):
        regasm = _find_dotnet_tool("RegAsm.exe")
        if regasm:
            result = subprocess.run(
                [regasm, dll_path, "/unregister", "/nologo"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print("  ✓ Unregistered COM shell extension via RegAsm")
                removed_anything = True
            else:
                print(f"  ⚠ RegAsm /unregister returned {result.returncode} — "
                      "falling back to direct registry cleanup")
        else:
            print("  ⚠ RegAsm.exe not found — falling back to direct registry cleanup")
    else:
        print(f"  - COM shell extension DLL not found ({dll_path}); "
              "proceeding with direct registry cleanup")

    # ── Step 3: direct registry cleanup (belt-and-suspenders) ────────────
    # These keys are created by [ComRegisterFunction] / RegAsm /codebase
    shellex_keys = [
        rf"SOFTWARE\Classes\*\shellex\ContextMenuHandlers\AEPGP",
        rf"SOFTWARE\Classes\Directory\Background\shellex\ContextMenuHandlers\AEPGP",
        rf"SOFTWARE\Classes\CLSID\{SHELL_EXT_CLSID}",
    ]
    for key_path in shellex_keys:
        try:
            winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            print(f"  ✓ Removed HKLM\\{key_path}")
            removed_anything = True
        except FileNotFoundError:
            pass  # Already absent
        except Exception as e:
            print(f"  ⚠ Could not remove HKLM\\{key_path}: {e}")

    # ── Step 4: remove installer-written key ─────────────────────────────
    try:
        winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\AEPGP\ContextMenu")
        print(r"  ✓ Removed HKLM\SOFTWARE\AEPGP\ContextMenu")
        removed_anything = True
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"  ⚠ Could not remove HKLM\\SOFTWARE\\AEPGP\\ContextMenu: {e}")

    # Clean up empty parent key if possible
    try:
        winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\AEPGP")
    except Exception:
        pass  # May still have subkeys; ignore

    return removed_anything


def uninstall_cascading_menus():
    """Remove all AEPGP cascading context menu entries"""
    success_count = 0

    print("\nRemoving COM shell extension...")
    if uninstall_com_shell_ext():
        success_count += 1

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


def delete_debug_log():
    """Delete the debug log file"""
    try:
        temp_dir = os.environ.get('TEMP', os.environ.get('TMP', 'C:\\Temp'))
        log_file = os.path.join(temp_dir, 'aepgp_debug.log')

        if os.path.exists(log_file):
            os.remove(log_file)
            print(f"  ✓ Deleted debug log: {log_file}")
            return True
        else:
            print(f"  - Debug log not found (already deleted or never created)")
            return True
    except Exception as e:
        print(f"  ! Warning: Could not delete debug log: {e}")
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
    log_deleted = delete_debug_log()

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
