"""
SmartPGP Context Menu - Setup Test Script

This script tests your system configuration to ensure everything is set up
correctly for the SmartPGP context menu integration.
"""

import sys
import os
import subprocess


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_result(test_name, passed, message=""):
    """Print a test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status} - {test_name}")
    if message:
        print(f"       {message}")


def test_python_version():
    """Test if Python version is adequate"""
    print_header("Testing Python Installation")

    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 7:
        print_result("Python Version", True, "Python 3.7+ detected")
        return True
    else:
        print_result("Python Version", False, "Python 3.7+ required")
        return False


def test_pyscard():
    """Test if pyscard is installed"""
    print_header("Testing pyscard Library")

    try:
        import smartcard
        from smartcard.System import readers
        print(f"pyscard version: {smartcard.__version__ if hasattr(smartcard, '__version__') else 'unknown'}")
        print_result("pyscard Import", True, "pyscard library found")
        return True
    except ImportError as e:
        print_result("pyscard Import", False, f"Install with: pip install pyscard")
        return False


def test_card_readers():
    """Test if smart card readers are available"""
    print_header("Testing Smart Card Readers")

    try:
        from smartcard.System import readers

        reader_list = readers()

        if not reader_list:
            print_result("Card Readers", False, "No smart card readers found")
            print("       Please connect a USB smart card reader")
            return False

        print(f"Found {len(reader_list)} reader(s):")
        for i, reader in enumerate(reader_list, 1):
            print(f"  {i}. {reader}")

        print_result("Card Readers", True, f"{len(reader_list)} reader(s) detected")
        return True

    except Exception as e:
        print_result("Card Readers", False, f"Error: {e}")
        return False


def test_smartpgp_card():
    """Test if SmartPGP card is present"""
    print_header("Testing SmartPGP Card")

    try:
        from smartcard.System import readers
        from smartcard.Exceptions import NoCardException

        reader_list = readers()
        if not reader_list:
            print_result("SmartPGP Card", False, "No readers available")
            return False

        # SmartPGP AID
        SMARTPGP_AID = [0xD2, 0x76, 0x00, 0x01, 0x24, 0x01]
        SELECT_APDU = [0x00, 0xA4, 0x04, 0x00, len(SMARTPGP_AID)] + SMARTPGP_AID + [0x00]

        for reader in reader_list:
            try:
                connection = reader.createConnection()
                connection.connect()

                # Try to select SmartPGP applet
                response, sw1, sw2 = connection.transmit(SELECT_APDU)

                if sw1 == 0x90 and sw2 == 0x00:
                    print(f"SmartPGP card found in: {reader}")
                    print_result("SmartPGP Card", True, "Card detected and responding")
                    connection.disconnect()
                    return True

                connection.disconnect()
            except NoCardException:
                continue
            except Exception:
                continue

        print_result("SmartPGP Card", False, "SmartPGP card not found in any reader")
        print("       Please insert your SmartPGP card")
        return False

    except Exception as e:
        print_result("SmartPGP Card", False, f"Error: {e}")
        return False


def test_gnupg():
    """Test if GnuPG is installed and accessible"""
    print_header("Testing GnuPG Installation")

    # Try to run gpg --version
    try:
        result = subprocess.run(
            ["gpg", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            # Extract version from first line
            first_line = result.stdout.split('\n')[0]
            print(first_line)
            print_result("GnuPG Installation", True, "gpg.exe found in PATH")
            return True
        else:
            print_result("GnuPG Installation", False, "gpg command failed")
            return False

    except FileNotFoundError:
        # Try common installation paths
        common_paths = [
            r"C:\Program Files (x86)\GnuPG\bin\gpg.exe",
            r"C:\Program Files\GnuPG\bin\gpg.exe",
        ]

        for path in common_paths:
            if os.path.exists(path):
                print(f"Found GnuPG at: {path}")
                print_result("GnuPG Installation", True, "But not in PATH")
                print("       Consider adding GnuPG to your system PATH")
                return True

        print_result("GnuPG Installation", False, "gpg.exe not found")
        print("       Install from: https://www.gpg4win.org/")
        return False

    except Exception as e:
        print_result("GnuPG Installation", False, f"Error: {e}")
        return False


def test_gpg_card_support():
    """Test if GnuPG can communicate with the card"""
    print_header("Testing GnuPG Card Support")

    try:
        result = subprocess.run(
            ["gpg", "--card-status"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0 and "Reader" in result.stdout:
            print("GnuPG can communicate with smart cards")

            # Check if it sees our card
            if "OpenPGP" in result.stdout or "SmartPGP" in result.stdout:
                print_result("GPG Card Support", True, "SmartPGP card recognized by GnuPG")
                return True
            else:
                print_result("GPG Card Support", True, "Card detected but may need initialization")
                print("       Run: gpg --card-edit")
                return True
        else:
            print_result("GPG Card Support", False, "GnuPG cannot detect card")
            print("       Make sure your SmartPGP card is inserted")
            return False

    except FileNotFoundError:
        print_result("GPG Card Support", False, "gpg.exe not found")
        return False
    except subprocess.TimeoutExpired:
        print_result("GPG Card Support", False, "Command timed out")
        return False
    except Exception as e:
        print_result("GPG Card Support", False, f"Error: {e}")
        return False


def test_context_menu_installed():
    """Test if context menu is installed in registry"""
    print_header("Testing Context Menu Installation")

    if sys.platform != 'win32':
        print_result("Context Menu", False, "Not on Windows")
        return False

    try:
        import winreg

        # Check encrypt menu
        try:
            key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\SmartPGP.Encrypt\command")
            value, _ = winreg.QueryValue(key, "")
            winreg.CloseKey(key)
            print(f"Encrypt menu: Installed")
            encrypt_ok = True
        except FileNotFoundError:
            print(f"Encrypt menu: NOT installed")
            encrypt_ok = False

        # Check decrypt menu
        try:
            key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r".gpg\shell\SmartPGP.Decrypt\command")
            value, _ = winreg.QueryValue(key, "")
            winreg.CloseKey(key)
            print(f"Decrypt menu: Installed")
            decrypt_ok = True
        except FileNotFoundError:
            print(f"Decrypt menu: NOT installed")
            decrypt_ok = False

        if encrypt_ok and decrypt_ok:
            print_result("Context Menu", True, "Both menu items installed")
            return True
        elif encrypt_ok or decrypt_ok:
            print_result("Context Menu", True, "Partially installed")
            print("       Run install_menu.py to complete installation")
            return True
        else:
            print_result("Context Menu", False, "Not installed")
            print("       Run install_menu.py to install")
            return False

    except Exception as e:
        print_result("Context Menu", False, f"Error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("  SmartPGP Context Menu - System Configuration Test")
    print("=" * 70)
    print("\nThis script will check if your system is properly configured.")

    results = []

    # Run all tests
    results.append(("Python Version", test_python_version()))
    results.append(("pyscard Library", test_pyscard()))
    results.append(("Card Readers", test_card_readers()))
    results.append(("SmartPGP Card", test_smartpgp_card()))
    results.append(("GnuPG Installation", test_gnupg()))
    results.append(("GPG Card Support", test_gpg_card_support()))
    results.append(("Context Menu", test_context_menu_installed()))

    # Summary
    print_header("Test Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {test_name}")

    print(f"\nPassed: {passed}/{total} tests")

    if passed == total:
        print("\n🎉 All tests passed! Your system is ready to use SmartPGP context menu.")
    else:
        print("\n⚠️  Some tests failed. Please address the issues above.")
        print("See README.md for troubleshooting help.")

    print("\n" + "=" * 70)
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
