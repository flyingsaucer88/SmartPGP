"""
AEPGP Windows Context Menu Installer - Cascading Menu Version

This script installs a cascading submenu structure for AEPGP operations.
All AEPGP options appear under a single "AEPGP" submenu.

IMPORTANT: This script requires Administrator privileges to modify the Windows
registry (HKEY_CLASSES_ROOT).
"""

import sys
import os
import winreg
import ctypes

# Version tracking
CURRENT_VERSION = "1.3.0"
VERSION_REG_KEY = r"Software\AEPGP\ContextMenu"
VERSION_VALUE_NAME = "Version"


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


def get_script_paths():
    """Get the absolute paths to the handler scripts"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    handlers_dir = os.path.join(script_dir, "handlers")

    encrypt_handler = os.path.join(handlers_dir, "encrypt_handler.py")
    decrypt_handler = os.path.join(handlers_dir, "decrypt_handler.py")
    generate_keys_handler = os.path.join(handlers_dir, "generate_keys_handler.py")
    delete_keys_handler = os.path.join(handlers_dir, "delete_keys_handler.py")
    # import_pfx_handler = os.path.join(handlers_dir, "import_pfx_handler.py")  # DISABLED - Feature incomplete
    change_pin_handler = os.path.join(handlers_dir, "change_pin_handler.py")

    # Verify handlers exist
    if not os.path.exists(encrypt_handler):
        raise FileNotFoundError(f"Encrypt handler not found: {encrypt_handler}")
    if not os.path.exists(decrypt_handler):
        raise FileNotFoundError(f"Decrypt handler not found: {decrypt_handler}")
    if not os.path.exists(generate_keys_handler):
        raise FileNotFoundError(f"Generate keys handler not found: {generate_keys_handler}")
    if not os.path.exists(delete_keys_handler):
        raise FileNotFoundError(f"Delete keys handler not found: {delete_keys_handler}")
    # if not os.path.exists(import_pfx_handler):  # DISABLED - Feature incomplete
    #     raise FileNotFoundError(f"Import PFX handler not found: {import_pfx_handler}")
    if not os.path.exists(change_pin_handler):
        raise FileNotFoundError(f"Change PIN handler not found: {change_pin_handler}")

    return encrypt_handler, decrypt_handler, generate_keys_handler, delete_keys_handler, change_pin_handler  # Removed import_pfx_handler


def install_cascading_menu_for_all_files(handlers):
    """
    Install flat menu items for all files (*).

    Creates individual menu items:
    Right-click any file →
        ├── AEPGP: Encrypt File
        ├── AEPGP: Decrypt File
        ├── AEPGP: Generate Keys
        ├── AEPGP: Delete Keys
        └── AEPGP: Change PIN
    """
    encrypt_handler, decrypt_handler, generate_keys_handler, delete_keys_handler, change_pin_handler = handlers

    try:
        python_exe = sys.executable.replace("python.exe", "pythonw.exe")
        if not os.path.exists(python_exe):
            python_exe = sys.executable

        # 1. AEPGP: Encrypt File
        encrypt_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\AEPGP_Encrypt")
        winreg.SetValueEx(encrypt_key, "MUIVerb", 0, winreg.REG_SZ, "AEPGP: Encrypt File")
        winreg.SetValueEx(encrypt_key, "Position", 0, winreg.REG_SZ, "Top")
        encrypt_cmd_key = winreg.CreateKey(encrypt_key, "command")
        winreg.SetValue(encrypt_cmd_key, "", winreg.REG_SZ, f'"{python_exe}" "{encrypt_handler}" "%1"')
        winreg.CloseKey(encrypt_cmd_key)
        winreg.CloseKey(encrypt_key)
        print("  ✓ Added 'AEPGP: Encrypt File'")

        # 2. AEPGP: Decrypt File
        decrypt_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\AEPGP_Decrypt")
        winreg.SetValueEx(decrypt_key, "MUIVerb", 0, winreg.REG_SZ, "AEPGP: Decrypt File")
        winreg.SetValueEx(decrypt_key, "Position", 0, winreg.REG_SZ, "Top")
        decrypt_cmd_key = winreg.CreateKey(decrypt_key, "command")
        winreg.SetValue(decrypt_cmd_key, "", winreg.REG_SZ, f'"{python_exe}" "{decrypt_handler}" "%1"')
        winreg.CloseKey(decrypt_cmd_key)
        winreg.CloseKey(decrypt_key)
        print("  ✓ Added 'AEPGP: Decrypt File'")

        # 3. AEPGP: Generate Keys
        genkeys_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\AEPGP_GenerateKeys")
        winreg.SetValueEx(genkeys_key, "MUIVerb", 0, winreg.REG_SZ, "AEPGP: Generate Keys")
        winreg.SetValueEx(genkeys_key, "Position", 0, winreg.REG_SZ, "Top")
        genkeys_cmd_key = winreg.CreateKey(genkeys_key, "command")
        winreg.SetValue(genkeys_cmd_key, "", winreg.REG_SZ, f'"{python_exe}" "{generate_keys_handler}"')
        winreg.CloseKey(genkeys_cmd_key)
        winreg.CloseKey(genkeys_key)
        print("  ✓ Added 'AEPGP: Generate Keys'")

        # 4. AEPGP: Delete Keys
        delkeys_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\AEPGP_DeleteKeys")
        winreg.SetValueEx(delkeys_key, "MUIVerb", 0, winreg.REG_SZ, "AEPGP: Delete Keys")
        winreg.SetValueEx(delkeys_key, "Position", 0, winreg.REG_SZ, "Top")
        delkeys_cmd_key = winreg.CreateKey(delkeys_key, "command")
        winreg.SetValue(delkeys_cmd_key, "", winreg.REG_SZ, f'"{python_exe}" "{delete_keys_handler}"')
        winreg.CloseKey(delkeys_cmd_key)
        winreg.CloseKey(delkeys_key)
        print("  ✓ Added 'AEPGP: Delete Keys'")

        # 5. AEPGP: Change PIN
        changepin_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\AEPGP_ChangePIN")
        winreg.SetValueEx(changepin_key, "MUIVerb", 0, winreg.REG_SZ, "AEPGP: Change PIN")
        winreg.SetValueEx(changepin_key, "Position", 0, winreg.REG_SZ, "Top")
        changepin_cmd_key = winreg.CreateKey(changepin_key, "command")
        winreg.SetValue(changepin_cmd_key, "", winreg.REG_SZ, f'"{python_exe}" "{change_pin_handler}"')
        winreg.CloseKey(changepin_cmd_key)
        winreg.CloseKey(changepin_key)
        print("  ✓ Added 'AEPGP: Change PIN'")

        # DISABLED - PFX Import feature incomplete
        # # 6. AEPGP: Import PFX (only for .pfx and .p12 files)
        # # Register for .pfx files
        # pfx_importkey = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r".pfx\shell\AEPGP_ImportPFX")
        # winreg.SetValueEx(pfx_importkey, "MUIVerb", 0, winreg.REG_SZ, "AEPGP: Import PFX to Card")
        # pfx_cmd_key = winreg.CreateKey(pfx_importkey, "command")
        # winreg.SetValue(pfx_cmd_key, "", winreg.REG_SZ, f'"{python_exe}" "{import_pfx_handler}" "%1"')
        # winreg.CloseKey(pfx_cmd_key)
        # winreg.CloseKey(pfx_importkey)
        #
        # # Register for .p12 files
        # p12_importkey = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r".p12\shell\AEPGP_ImportPFX")
        # winreg.SetValueEx(p12_importkey, "MUIVerb", 0, winreg.REG_SZ, "AEPGP: Import PFX to Card")
        # p12_cmd_key = winreg.CreateKey(p12_importkey, "command")
        # winreg.SetValue(p12_cmd_key, "", winreg.REG_SZ, f'"{python_exe}" "{import_pfx_handler}" "%1"')
        # winreg.CloseKey(p12_cmd_key)
        # winreg.CloseKey(p12_importkey)
        # print("  ✓ Added 'AEPGP: Import PFX' for .pfx and .p12 files")

        print("✓ Installed AEPGP cascading menu for all files")
        return True

    except Exception as e:
        print(f"✗ Failed to install cascading menu: {e}")
        import traceback
        traceback.print_exc()
        return False


def install_cascading_menu_for_desktop(handlers):
    """
    Install cascading submenu for Desktop background.

    Creates structure:
    Right-click Desktop → AEPGP →
        ├── Generate Keys in Card
        ├── Delete Keys from Card
        └── Change Card PIN
    """
    _, _, generate_keys_handler, delete_keys_handler, _, change_pin_handler = handlers

    try:
        python_exe = sys.executable.replace("python.exe", "pythonw.exe")
        if not os.path.exists(python_exe):
            python_exe = sys.executable

        # Create main AEPGP submenu for desktop background
        main_key_path = r"Directory\Background\shell\AEPGP"
        main_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, main_key_path)

        # Set submenu text and make it a cascading menu
        winreg.SetValueEx(main_key, "MUIVerb", 0, winreg.REG_SZ, "AEPGP")
        # Empty SubCommands tells Windows to use shell subkeys
        winreg.SetValueEx(main_key, "SubCommands", 0, winreg.REG_SZ, "")

        # Create shell subkey for submenu items
        shell_key = winreg.CreateKey(main_key, "shell")

        # 1. Generate Keys in Card
        genkeys_key = winreg.CreateKey(shell_key, "generatekeys")
        winreg.SetValueEx(genkeys_key, "", 0, winreg.REG_SZ, "Generate Keys in Card")
        winreg.SetValueEx(genkeys_key, "MUIVerb", 0, winreg.REG_SZ, "Generate Keys in Card")
        genkeys_cmd_key = winreg.CreateKey(genkeys_key, "command")
        winreg.SetValue(genkeys_cmd_key, "", winreg.REG_SZ, f'"{python_exe}" "{generate_keys_handler}"')
        winreg.CloseKey(genkeys_cmd_key)
        winreg.CloseKey(genkeys_key)
        print("  ✓ Added 'Generate Keys in Card' to desktop menu")

        # 2. Delete Keys from Card
        delkeys_key = winreg.CreateKey(shell_key, "deletekeys")
        winreg.SetValueEx(delkeys_key, "", 0, winreg.REG_SZ, "Delete Keys from Card")
        winreg.SetValueEx(delkeys_key, "MUIVerb", 0, winreg.REG_SZ, "Delete Keys from Card")
        delkeys_cmd_key = winreg.CreateKey(delkeys_key, "command")
        winreg.SetValue(delkeys_cmd_key, "", winreg.REG_SZ, f'"{python_exe}" "{delete_keys_handler}"')
        winreg.CloseKey(delkeys_cmd_key)
        winreg.CloseKey(delkeys_key)
        print("  ✓ Added 'Delete Keys from Card' to desktop menu")

        # 3. Change Card PIN
        changepin_key = winreg.CreateKey(shell_key, "changepin")
        winreg.SetValueEx(changepin_key, "", 0, winreg.REG_SZ, "Change Card PIN")
        winreg.SetValueEx(changepin_key, "MUIVerb", 0, winreg.REG_SZ, "Change Card PIN")
        changepin_cmd_key = winreg.CreateKey(changepin_key, "command")
        winreg.SetValue(changepin_cmd_key, "", winreg.REG_SZ, f'"{python_exe}" "{change_pin_handler}"')
        winreg.CloseKey(changepin_cmd_key)
        winreg.CloseKey(changepin_key)
        print("  ✓ Added 'Change Card PIN' to desktop menu")

        winreg.CloseKey(shell_key)
        winreg.CloseKey(main_key)

        print("✓ Installed AEPGP cascading menu for desktop background")
        return True

    except Exception as e:
        print(f"✗ Failed to install desktop cascading menu: {e}")
        import traceback
        traceback.print_exc()
        return False


def set_installed_version(version):
    """Store the installed version in registry."""
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, VERSION_REG_KEY)
        winreg.SetValueEx(key, VERSION_VALUE_NAME, 0, winreg.REG_SZ, version)
        winreg.CloseKey(key)
        print(f"✓ Registered version: {version}")
    except Exception as e:
        print(f"Warning: Could not store version: {e}")


def create_debug_log():
    """Create a fresh debug log file"""
    try:
        temp_dir = os.environ.get('TEMP', os.environ.get('TMP', 'C:\\Temp'))
        log_file = os.path.join(temp_dir, 'aepgp_debug.log')

        # Remove old log if it exists
        if os.path.exists(log_file):
            os.remove(log_file)

        # Create empty log file
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"AEPGP Debug Log\n")
            f.write(f"Created during installation of version {CURRENT_VERSION}\n")
            f.write(f"{'=' * 80}\n\n")

        print(f"  ✓ Created debug log: {log_file}")
        return True
    except Exception as e:
        print(f"  ! Warning: Could not create debug log: {e}")
        return False


def main():
    """Main installation function"""
    print("=" * 70)
    print("AEPGP Windows Context Menu Installer - Cascading Menu Version")
    print(f"Version {CURRENT_VERSION}")
    print("=" * 70)

    # Check if running on Windows
    if sys.platform != 'win32':
        print("\nERROR: This installer is only for Windows operating systems.")
        print("Press Enter to exit...")
        input()
        sys.exit(1)

    # Check for admin privileges
    if not is_admin():
        print("\nThis installer requires Administrator privileges.")
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

    # Get handler script paths
    try:
        handlers = get_script_paths()
        encrypt_handler, decrypt_handler, generate_keys_handler, delete_keys_handler, change_pin_handler = handlers
        print(f"\nFound encrypt handler: {encrypt_handler}")
        print(f"Found decrypt handler: {decrypt_handler}")
        print(f"Found generate keys handler: {generate_keys_handler}")
        print(f"Found delete keys handler: {delete_keys_handler}")
        # print(f"Found import PFX handler: {import_pfx_handler}")  # DISABLED
        print(f"Found change PIN handler: {change_pin_handler}")
    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)

    # Install menu items
    print("\n" + "=" * 70)
    print("Installing AEPGP cascading context menu...")
    print("=" * 70)

    all_files_ok = install_cascading_menu_for_all_files(handlers)
    desktop_ok = install_cascading_menu_for_desktop(handlers)

    # Create fresh debug log file
    create_debug_log()

    # Store version information
    if all_files_ok and desktop_ok:
        set_installed_version(CURRENT_VERSION)

    # Summary
    print("\n" + "=" * 70)
    if all_files_ok and desktop_ok:
        print("Installation completed successfully! ✓")
        print(f"\nInstalled version: {CURRENT_VERSION}")
        print("\nHow to use:")
        print("  1. Right-click any file → AEPGP → Choose action")
        print("  2. Right-click Desktop → AEPGP → Generate Keys or Change PIN")
        print("\nAvailable actions in AEPGP submenu:")
        print("  • Encrypt File")
        print("  • Decrypt File")
        print("  • Generate Keys in Card")
        print("  • Change Card PIN")
        print("\nNOTE: On Windows 11, AEPGP appears in 'Show more options'")
        print("      (or you can use SHIFT+Right-click)")
    else:
        print("Installation completed with errors.")
        print("Some context menu items may not have been installed.")
        if not all_files_ok:
            print("  ✗ File context menu failed")
        if not desktop_ok:
            print("  ✗ Desktop context menu failed")

    print("\nPress Enter to exit...")
    input()


if __name__ == "__main__":
    main()
