"""
AEPGP Windows Context Menu Installer

This script installs Windows Explorer context menu entries for encrypting and
decrypting files with AEPGP cards.

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


def get_script_paths():
    """Get the absolute paths to the handler scripts"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    handlers_dir = os.path.join(script_dir, "handlers")

    encrypt_handler = os.path.join(handlers_dir, "encrypt_handler.py")
    decrypt_handler = os.path.join(handlers_dir, "decrypt_handler.py")

    # Verify handlers exist
    if not os.path.exists(encrypt_handler):
        raise FileNotFoundError(f"Encrypt handler not found: {encrypt_handler}")
    if not os.path.exists(decrypt_handler):
        raise FileNotFoundError(f"Decrypt handler not found: {decrypt_handler}")

    return encrypt_handler, decrypt_handler


def install_encrypt_menu(encrypt_handler):
    """
    Install the "Encrypt with AEPGP" context menu item for all files.

    Args:
        encrypt_handler: Path to encrypt_handler.py
    """
    try:
        # Create registry key for all files (*)
        key_path = r"*\shell\AEPGP.Encrypt"
        key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path)

        # Set the menu text
        winreg.SetValue(key, "", winreg.REG_SZ, "Encrypt with AEPGP")

        # Create the command subkey
        cmd_key = winreg.CreateKey(key, "command")

        # Set the command to execute
        # Use pythonw.exe to avoid showing a console window
        python_exe = sys.executable.replace("python.exe", "pythonw.exe")
        if not os.path.exists(python_exe):
            python_exe = sys.executable  # Fall back to python.exe

        command = f'"{python_exe}" "{encrypt_handler}" "%1"'
        winreg.SetValue(cmd_key, "", winreg.REG_SZ, command)

        winreg.CloseKey(cmd_key)
        winreg.CloseKey(key)

        print(f"✓ Installed 'Encrypt with AEPGP' menu item")
        return True

    except Exception as e:
        print(f"✗ Failed to install encrypt menu: {e}")
        return False


def install_decrypt_menu(decrypt_handler):
    """
    Install the "Decrypt with AEPGP" context menu item for encrypted files.

    Args:
        decrypt_handler: Path to decrypt_handler.py
    """
    try:
        # Python exe (use pythonw to avoid console window)
        python_exe = sys.executable.replace("python.exe", "pythonw.exe")
        if not os.path.exists(python_exe):
            python_exe = sys.executable

        # Install for multiple encrypted file extensions
        extensions = [".gpg", ".pgp", ".asc"]
        success_count = 0

        for ext in extensions:
            try:
                # Create registry key for this extension
                key_path = f"{ext}\\shell\\AEPGP.Decrypt"
                key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path)

                # Set the menu text
                winreg.SetValue(key, "", winreg.REG_SZ, "Decrypt with AEPGP")

                # Create the command subkey
                cmd_key = winreg.CreateKey(key, "command")

                # Set the command to execute
                command = f'"{python_exe}" "{decrypt_handler}" "%1"'
                winreg.SetValue(cmd_key, "", winreg.REG_SZ, command)

                winreg.CloseKey(cmd_key)
                winreg.CloseKey(key)

                print(f"✓ Installed 'Decrypt with AEPGP' for {ext} files")
                success_count += 1

            except Exception as e:
                print(f"✗ Failed to install decrypt menu for {ext}: {e}")

        return success_count > 0

    except Exception as e:
        print(f"✗ Failed to install decrypt menu: {e}")
        return False


def verify_installation():
    """Verify that the context menu entries were installed correctly"""
    try:
        # Check encrypt menu
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\AEPGP.Encrypt\command")
        value, _ = winreg.QueryValue(key, "")
        winreg.CloseKey(key)
        print(f"\nEncrypt menu command: {value}")

        # Check decrypt menu for .gpg
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r".gpg\shell\AEPGP.Decrypt\command")
        value, _ = winreg.QueryValue(key, "")
        winreg.CloseKey(key)
        print(f"Decrypt menu command: {value}")

        return True
    except Exception as e:
        print(f"\nWarning: Could not verify installation: {e}")
        return False


def main():
    """Main installation function"""
    print("=" * 70)
    print("AEPGP Windows Context Menu Installer")
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
        encrypt_handler, decrypt_handler = get_script_paths()
        print(f"\nFound encrypt handler: {encrypt_handler}")
        print(f"Found decrypt handler: {decrypt_handler}")
    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)

    # Install menu items
    print("\n" + "=" * 70)
    print("Installing context menu items...")
    print("=" * 70)

    encrypt_ok = install_encrypt_menu(encrypt_handler)
    decrypt_ok = install_decrypt_menu(decrypt_handler)

    # Verify installation
    print("\n" + "=" * 70)
    print("Verifying installation...")
    print("=" * 70)
    verify_installation()

    # Summary
    print("\n" + "=" * 70)
    if encrypt_ok and decrypt_ok:
        print("Installation completed successfully! ✓")
        print("\nYou can now:")
        print("  1. Right-click any file → 'Encrypt with AEPGP'")
        print("  2. Right-click .gpg/.pgp/.asc files → 'Decrypt with AEPGP'")
        print("\nNOTE: On Windows 11, these options appear in 'Show more options'")
        print("      (or you can use SHIFT+Right-click)")
    else:
        print("Installation completed with errors.")
        print("Some context menu items may not have been installed.")

    print("\nPress Enter to exit...")
    input()


if __name__ == "__main__":
    main()
