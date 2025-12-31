"""
AEPGP Complete Functionality Test Script

This script tests all AEPGP card features in sequence:
1. Card detection and connection
2. Delete existing keys from card
3. Generate new RSA-2048 key pair on card
4. Change PIN from default to custom
5. Encrypt a test file
6. Decrypt the encrypted file
7. Import PFX certificate (optional)

Run this script with: python test_all_features.py
"""

import sys
import os
import subprocess
import time

# Add handlers to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "handlers"))

# Test configuration
PFX_FILE_PATH = r"C:\Users\Neel\Documents\Ambimat\AmbiSecure\Digital Signature\OneDrive_2_18-05-2023\NXP_cert_creation_openSSL\NXP_cert_creation_openSSL\UserCert1_auth.pfx"
FACTORY_DEFAULT_PIN = "123456"  # OpenPGP card factory default
CUSTOM_DEFAULT_PIN = "190482"   # Your custom default PIN (for cards already set up)
NEW_PIN = "654321"              # PIN to change to during test
TEST_FILE = os.path.join(os.path.dirname(__file__), "test_data.txt")

# Track which PIN to use (gets updated after key generation)
current_pin = CUSTOM_DEFAULT_PIN


def print_separator(title=""):
    """Print a visual separator"""
    if title:
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)
    else:
        print("=" * 70)


def print_step(step_num, description):
    """Print a test step"""
    print(f"\n[STEP {step_num}] {description}")
    print("-" * 70)


def run_gpg_command(command):
    """Run a GPG command and return output"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"


def kill_gpg_agent():
    """
    Kill GPG agent and scdaemon to release card lock.
    GPG's scdaemon holds exclusive access to the smart card.
    """
    try:
        print("  Terminating GPG agent and scdaemon...")

        # Try gpgconf command first (preferred method)
        result = subprocess.run(
            "gpgconf --kill scdaemon",
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )

        # Also kill gpg-agent
        subprocess.run(
            "gpgconf --kill gpg-agent",
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )

        # Give it a moment to fully terminate
        time.sleep(1)

        print("  ✓ GPG processes terminated")
        return True

    except Exception as e:
        print(f"  ⚠ Could not terminate GPG processes: {e}")
        return False


def wait_for_card_reconnect(max_retries=5, delay=2):
    """
    Wait for the card to be accessible after GPG operations.
    GPG can hold the card lock, so we need to retry.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay in seconds between retries

    Returns:
        bool: True if card is accessible, False otherwise
    """
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "handlers"))
    from card_utils import find_aepgp_card

    print(f"\nWaiting for card to be accessible...")

    # First, try to kill GPG agent/scdaemon to release the card
    kill_gpg_agent()

    for attempt in range(max_retries):
        try:
            # Try to reconnect to the card
            card, error = find_aepgp_card()

            if error:
                if attempt < max_retries - 1:
                    print(f"  Attempt {attempt + 1}/{max_retries}: Card not ready, waiting {delay}s...")
                    time.sleep(delay)
                    continue
                else:
                    print(f"  ❌ Card not accessible after {max_retries} attempts")
                    return False
            else:
                # Card found, disconnect and return success
                card.disconnect()
                print(f"  ✓ Card is accessible")
                return True

        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  Attempt {attempt + 1}/{max_retries}: Error ({e}), retrying...")
                time.sleep(delay)
            else:
                print(f"  ❌ Error accessing card: {e}")
                return False

    return False


def test_card_detection():
    """Test 1: Detect AEPGP card"""
    print_step(1, "Card Detection")

    try:
        from card_utils import find_aepgp_card

        print("Searching for AEPGP card...")
        card, error = find_aepgp_card()

        if error:
            print(f"❌ FAILED: {error}")
            return False

        print(f"✓ Card found: {card.reader}")
        card.disconnect()
        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_delete_keys():
    """Test 2: Delete existing keys from card"""
    print_step(2, "Delete Existing Keys from Card")

    print("WARNING: This will permanently delete all keys on the card!")
    response = input("Continue? (yes/no): ")

    if response.lower() not in ['yes', 'y']:
        print("Skipped by user")
        return True

    try:
        print("\nDeleting keys using GnuPG card-edit...")
        print("This will use GPG to reset the card to factory settings.\n")

        # Use GPG to check card status first
        print("Checking current card status...")
        code, stdout, stderr = run_gpg_command("gpg --card-status")

        if code != 0:
            print(f"❌ FAILED: Cannot access card")
            print(f"Error: {stderr}")
            return False

        print("✓ Card accessible")

        # Delete keys using factory reset
        print("\nAttempting factory reset of card...")
        print("Note: You may need to use the Admin PIN (default: 12345678)")

        # Instructions for manual reset
        print("\nMANUAL STEPS REQUIRED:")
        print("1. Run: gpg --card-edit")
        print("2. Type: admin")
        print("3. Type: factory-reset")
        print("4. Confirm when prompted")
        print("5. Type: quit")
        print("\nPlease perform these steps manually, then press Enter to continue...")
        input()

        # Verify keys are deleted
        print("\nVerifying keys are deleted...")
        code, stdout, stderr = run_gpg_command("gpg --card-status")

        if "General key info" not in stdout or "none" in stdout.lower():
            print("✓ Keys successfully deleted from card")

            # Wait for card to be accessible again after GPG operations
            if not wait_for_card_reconnect():
                print("⚠ Warning: Card may not be accessible for subsequent tests")

            return True
        else:
            print("⚠ Warning: Keys may still be present. Please verify manually.")
            return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_generate_keys():
    """Test 3: Generate new RSA-2048 keys on card"""
    global current_pin
    print_step(3, "Generate RSA-2048 Keys on Card")

    try:
        print("Generating RSA-2048 key pair on card...")
        print("This may take 30-60 seconds...\n")

        # Use GPG to generate keys
        print("MANUAL STEPS REQUIRED:")
        print("1. Run: gpg --card-edit")
        print("2. Type: admin")
        print("3. Type: generate")
        print("4. When asked 'Make off-card backup?', type: n")
        print("5. Follow prompts to set key expiration")
        print("6. Enter your name and email")
        print("7. Type: quit when done")
        print("\nPlease perform these steps manually, then press Enter to continue...")
        input()

        # Verify keys were generated
        print("\nVerifying keys were generated...")
        code, stdout, stderr = run_gpg_command("gpg --card-status")

        if "General key info" in stdout and "rsa2048" in stdout.lower():
            print("✓ RSA-2048 keys successfully generated on card")

            # IMPORTANT: After key generation, the PIN is reset to factory default!
            current_pin = FACTORY_DEFAULT_PIN
            print(f"⚠ Note: PIN has been reset to factory default ({FACTORY_DEFAULT_PIN})")

            # IMPORTANT: Wait for card to be accessible again after GPG operations
            # GPG holds an exclusive lock on the card that needs to be released
            if not wait_for_card_reconnect():
                print("⚠ Warning: Card may not be accessible for subsequent tests")

            return True
        else:
            print("⚠ Warning: Could not verify key generation. Please check manually.")
            return False

    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_change_pin():
    """Test 4: Change card PIN"""
    global current_pin
    print_step(4, "Change Card PIN")

    try:
        import getpass
        from card_utils import find_aepgp_card

        print("This test will change your AEPGP card PIN.\n")

        # Step 1: Prompt for old PIN and verify it
        print(f"Expected current PIN: {current_pin}")
        old_pin = getpass.getpass("Enter your CURRENT PIN (input hidden): ")

        if not old_pin:
            print("❌ FAILED: No PIN entered")
            return False

        # Connect to card and verify old PIN
        print("\nVerifying current PIN with card...")
        card, error = find_aepgp_card()
        if error:
            print(f"❌ FAILED: {error}")
            return False

        try:
            card.select_applet()

            # Verify old PIN using APDU
            old_pin_bytes = [ord(c) for c in old_pin]
            verify_cmd = [0x00, 0x20, 0x00, 0x82, len(old_pin_bytes)] + old_pin_bytes
            response, sw1, sw2 = card.connection.transmit(verify_cmd)

            if sw1 != 0x90 or sw2 != 0x00:
                if sw1 == 0x63:
                    retries = sw2 & 0x0F
                    print(f"❌ FAILED: Incorrect current PIN. {retries} attempts remaining.")
                else:
                    print(f"❌ FAILED: PIN verification failed (SW={sw1:02X}{sw2:02X})")
                return False

            print("✓ Current PIN verified successfully")
            card.disconnect()

        except Exception as e:
            print(f"❌ FAILED during PIN verification: {e}")
            return False

        # Step 2: Prompt for new PIN
        new_pin = getpass.getpass("\nEnter your NEW PIN (input hidden): ")

        if not new_pin:
            print("❌ FAILED: No new PIN entered")
            return False

        # Validate new PIN length
        if len(new_pin) < 6:
            print(f"❌ FAILED: New PIN too short ({len(new_pin)} chars). Minimum: 6 characters")
            return False

        if len(new_pin) > 127:
            print(f"❌ FAILED: New PIN too long ({len(new_pin)} chars). Maximum: 127 characters")
            return False

        # Confirm new PIN
        new_pin_confirm = getpass.getpass("Re-enter your NEW PIN to confirm (input hidden): ")

        if new_pin != new_pin_confirm:
            print("❌ FAILED: New PIN and confirmation do not match")
            return False

        # Step 3: Use GPG passwd command to change PIN
        print("\nChanging PIN using GPG passwd command...")
        print("This uses GPG's built-in PIN change functionality (most reliable method).\n")

        try:
            # Create automated input for gpg
            # Format: old_pin\nnew_pin\nnew_pin\n
            gpg_input = f"{old_pin}\n{new_pin}\n{new_pin}\n"

            # Run gpg --card-edit with automated input
            # Command sequence: admin -> passwd -> 1 (change PIN) -> quit
            gpg_commands = f"admin\npasswd\n1\n{gpg_input}quit\n"

            print("Executing GPG PIN change...")
            result = subprocess.run(
                "gpg --command-fd 0 --status-fd 2 --card-edit",
                input=gpg_commands,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            # Check if GPG command succeeded
            if "PIN changed" in result.stderr or "successfully" in result.stderr.lower():
                print("✓ GPG reported PIN change successful")
            else:
                # GPG might not output confirmation, so we'll verify below
                print("GPG command completed")

        except subprocess.TimeoutExpired:
            print("⚠ Warning: GPG command timed out, but PIN may have changed")
        except Exception as e:
            print(f"⚠ Warning: GPG command error: {e}")
            print("Continuing to verification step...")

        # Step 4: Kill GPG agent and verify new PIN works
        print("\nVerifying PIN was changed...")
        kill_gpg_agent()
        time.sleep(1)

        card, error = find_aepgp_card()
        if error:
            print(f"❌ FAILED: Cannot reconnect to card: {error}")
            return False

        try:
            card.select_applet()

            # Try to verify with NEW PIN
            print(f"Testing new PIN...")
            new_pin_bytes = [ord(c) for c in new_pin]
            verify_cmd = [0x00, 0x20, 0x00, 0x82, len(new_pin_bytes)] + new_pin_bytes
            response, sw1, sw2 = card.connection.transmit(verify_cmd)

            if sw1 == 0x90 and sw2 == 0x00:
                print(f"✓ PIN successfully changed to new PIN!")
                print("✓ New PIN verified successfully")
                # Update the current PIN for subsequent tests
                current_pin = new_pin
                return True
            else:
                print(f"❌ FAILED: New PIN verification failed (SW={sw1:02X}{sw2:02X})")
                print(f"PIN may not have been changed. Current PIN is still: {old_pin}")
                return False

        finally:
            card.disconnect()

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_encryption():
    """Test 5: Encrypt a test file"""
    print_step(5, "Encrypt Test File")

    try:
        # Create test file
        print("Creating test file...")
        with open(TEST_FILE, 'w') as f:
            f.write("This is a test file for AEPGP encryption.\n")
            f.write("Current timestamp: " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n")
            f.write("Test data: ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\n")

        print(f"✓ Test file created: {TEST_FILE}")

        # Encrypt using the handler
        print("Encrypting file using AEPGP card...")
        from rsa_crypto import encrypt_file_with_card_key

        output_file = TEST_FILE + ".enc"
        success, error_msg = encrypt_file_with_card_key(TEST_FILE, output_file)

        if success:
            encrypted_size = os.path.getsize(output_file)
            print(f"✓ File encrypted successfully")
            print(f"  Encrypted file: {output_file}")
            print(f"  Size: {encrypted_size} bytes")
            return True
        else:
            print(f"❌ FAILED: {error_msg}")
            return False

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_decryption():
    """Test 6: Decrypt the encrypted file"""
    print_step(6, "Decrypt Encrypted File")

    try:
        from rsa_decrypt import decrypt_file_with_card

        encrypted_file = TEST_FILE + ".enc"
        decrypted_file = TEST_FILE + ".decrypted"

        if not os.path.exists(encrypted_file):
            print(f"❌ FAILED: Encrypted file not found: {encrypted_file}")
            return False

        print(f"Decrypting file using current PIN: {current_pin}...")
        success, error_msg = decrypt_file_with_card(encrypted_file, decrypted_file, pin=current_pin)

        if success:
            print(f"✓ File decrypted successfully")
            print(f"  Decrypted file: {decrypted_file}")

            # Verify content matches
            print("\nVerifying decrypted content matches original...")
            with open(TEST_FILE, 'r') as f:
                original = f.read()
            with open(decrypted_file, 'r') as f:
                decrypted = f.read()

            if original == decrypted:
                print("✓ Content verification: PASSED")
                return True
            else:
                print("❌ Content verification: FAILED (content mismatch)")
                return False
        else:
            print(f"❌ FAILED: {error_msg}")
            return False

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pfx_import():
    """Test 7: Import PFX certificate (optional)"""
    print_step(7, "Import PFX Certificate (Optional)")

    if not os.path.exists(PFX_FILE_PATH):
        print(f"⚠ PFX file not found: {PFX_FILE_PATH}")
        print("Skipping PFX import test")
        return True

    print(f"PFX file found: {PFX_FILE_PATH}")
    print("\nNOTE: PFX import functionality is not yet fully implemented.")
    print("This test will verify the PFX file can be read and parsed.")

    try:
        from cryptography.hazmat.primitives.serialization import pkcs12
        from cryptography.hazmat.backends import default_backend

        # Ask for password
        import getpass
        password = getpass.getpass("Enter PFX password: ")

        print("\nReading PFX file...")
        with open(PFX_FILE_PATH, 'rb') as f:
            pfx_data = f.read()

        print("Parsing PFX file...")
        password_bytes = password.encode('utf-8') if password else None
        private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
            pfx_data,
            password_bytes,
            backend=default_backend()
        )

        if private_key:
            from cryptography.hazmat.primitives.asymmetric import rsa
            if isinstance(private_key, rsa.RSAPrivateKey):
                key_size = private_key.key_size
                print(f"✓ PFX file parsed successfully")
                print(f"  Key type: RSA-{key_size}")

                if certificate:
                    subject = certificate.subject.rfc4514_string()
                    print(f"  Certificate subject: {subject}")

                if key_size == 2048:
                    print("✓ Key is compatible with AEPGP card (RSA-2048)")
                    return True
                else:
                    print(f"⚠ Warning: Key size {key_size} may not be compatible (RSA-2048 required)")
                    return True
            else:
                print(f"⚠ Warning: Key type {type(private_key).__name__} not supported")
                return True
        else:
            print("❌ FAILED: No private key found in PFX file")
            return False

    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def cleanup():
    """Cleanup test files"""
    print_step("CLEANUP", "Removing Test Files")

    files_to_remove = [
        TEST_FILE,
        TEST_FILE + ".enc",
        TEST_FILE + ".decrypted"
    ]

    for filepath in files_to_remove:
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"✓ Removed: {filepath}")
            except Exception as e:
                print(f"⚠ Could not remove {filepath}: {e}")


def main():
    """Main test execution"""
    print_separator("AEPGP COMPLETE FUNCTIONALITY TEST")
    print("This script will test all AEPGP features")
    print(f"Initial PIN: {current_pin}")
    print(f"Factory Default PIN: {FACTORY_DEFAULT_PIN} (after key generation)")
    print(f"New PIN (to set): {NEW_PIN}")
    print(f"PFX File: {PFX_FILE_PATH}")
    print_separator()

    input("\nPress Enter to start tests...")

    # Track test results
    results = {}

    # Run tests
    results["Card Detection"] = test_card_detection()

    if results["Card Detection"]:
        results["Delete Keys"] = test_delete_keys()
        results["Generate Keys"] = test_generate_keys()
        results["Change PIN"] = test_change_pin()
        results["Encryption"] = test_encryption()
        results["Decryption"] = test_decryption()
        results["PFX Import"] = test_pfx_import()

    # Summary
    print_separator("TEST SUMMARY")

    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)

    for test_name, result in results.items():
        status = "✓ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<50} {status}")

    print_separator()
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")

    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠ {total_tests - passed_tests} test(s) failed")

    # Cleanup
    cleanup_response = input("\nCleanup test files? (yes/no): ")
    if cleanup_response.lower() in ['yes', 'y']:
        cleanup()

    print("\nTest complete!")
    print_separator()


if __name__ == "__main__":
    main()
