"""
AEPGP File Encryption Handler

This script is called when the user right-clicks a file and selects
"Encrypt with AEPGP" from the context menu.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add parent directory to path to import card_utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import card_utils
from debug_logger import get_logger

# Initialize logger
logger = get_logger()


def find_gpg_executable():
    """
    Find the GnuPG executable on the system.

    Returns:
        str: Path to gpg.exe or None if not found
    """
    # Common GnuPG installation paths on Windows
    possible_paths = [
        r"C:\Program Files (x86)\GnuPG\bin\gpg.exe",
        r"C:\Program Files\GnuPG\bin\gpg.exe",
        r"C:\Program Files (x86)\GNU\GnuPG\gpg.exe",
        r"C:\Program Files\GNU\GnuPG\gpg.exe",
    ]

    # Check if gpg is in PATH
    try:
        result = subprocess.run(["gpg", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            return "gpg"
    except FileNotFoundError:
        pass

    # Check common installation paths
    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


def get_card_key_info(card):
    """
    Get the public key information from the AEPGP card.

    Args:
        card: AEPGPCard object

    Returns:
        str: Key ID or fingerprint for encryption
    """
    # For now, we'll let GPG auto-detect the card key
    # In a more advanced implementation, you could query the card directly
    return None


def encrypt_file(filepath):
    """
    Encrypt a file using GnuPG with the AEPGP card.

    Args:
        filepath: Path to the file to encrypt
    """
    logger.log_operation_start("Encryption", filepath)
    logger.log_system_info()

    # Verify file exists
    if not os.path.exists(filepath):
        logger.error(f"File not found: {filepath}")
        card_utils.show_error_dialog(
            f"File not found:\n{filepath}",
            "AEPGP Encryption Error"
        )
        logger.log_operation_end("Encryption", False, "File not found")
        return

    logger.info(f"File exists, size: {os.path.getsize(filepath)} bytes")

    # Check for AEPGP card
    logger.info("Searching for AEPGP card...")
    card, error = card_utils.find_aepgp_card()
    if error:
        logger.error(f"Card detection failed: {error}")
        logger.log_card_detection(0, False)
        card_utils.show_error_dialog(
            f"Cannot encrypt file:\n\n{error}",
            "AEPGP Card Not Found"
        )
        logger.log_operation_end("Encryption", False, "Card not found")
        return

    # Log card detection success
    try:
        from smartcard.util import toHexString
        atr = card.connection.getATR()
        atr_hex = toHexString(atr)
        logger.log_card_detection(1, True, atr_hex)
        logger.info(f"Card found in reader: {card.reader}")
    except Exception as e:
        logger.warning(f"Could not get card ATR: {e}")

    # Card found, disconnect as GPG will handle the connection
    card.disconnect()
    logger.info("Card connection closed (GPG will reconnect)")

    # Find GnuPG
    logger.info("Searching for GnuPG executable...")
    gpg_path = find_gpg_executable()
    if not gpg_path:
        logger.error("GnuPG not found on system")
        card_utils.show_error_dialog(
            "GnuPG (gpg.exe) not found on your system.\n\n"
            "Please install GnuPG from:\n"
            "https://www.gnupg.org/download/\n\n"
            "Or install Gpg4win from:\n"
            "https://www.gpg4win.org/",
            "GnuPG Not Found"
        )
        logger.log_operation_end("Encryption", False, "GnuPG not found")
        return

    logger.info(f"Found GnuPG at: {gpg_path}")

    # Prepare output filename
    output_path = filepath + ".gpg"

    # Check if output file already exists
    if os.path.exists(output_path):
        overwrite = card_utils.show_question_dialog(
            f"The encrypted file already exists:\n\n{output_path}\n\n"
            "Do you want to overwrite it?",
            "File Already Exists"
        )
        if not overwrite:
            return

    try:
        # Build GPG command
        # Using --symmetric for password-based encryption
        # Or use --encrypt --recipient if you want public key encryption
        cmd = [
            gpg_path,
            "--armor",  # ASCII armored output (optional)
            "--output", output_path,
            "--encrypt",
            "--sign",  # Sign and encrypt
            filepath
        ]

        logger.info(f"Executing GPG command: {' '.join(cmd)}")

        # Run GPG (this will prompt for PIN via pinentry)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )

        logger.debug(f"GPG return code: {result.returncode}")
        if result.stdout:
            logger.debug(f"GPG stdout: {result.stdout}")
        if result.stderr:
            logger.debug(f"GPG stderr: {result.stderr}")

        if result.returncode == 0:
            # Success!
            logger.info(f"Encryption successful, output: {output_path}")
            card_utils.show_info_dialog(
                f"File encrypted successfully!\n\n"
                f"Original: {os.path.basename(filepath)}\n"
                f"Encrypted: {os.path.basename(output_path)}\n\n"
                f"Location: {os.path.dirname(output_path)}",
                "Encryption Successful"
            )
            logger.log_operation_end("Encryption", True)
        else:
            # Encryption failed
            error_msg = result.stderr if result.stderr else "Unknown error"
            logger.error(f"GPG encryption failed: {error_msg}")
            card_utils.show_error_dialog(
                f"Encryption failed:\n\n{error_msg}",
                "Encryption Error"
            )
            logger.log_operation_end("Encryption", False, error_msg)

    except Exception as e:
        logger.error("Exception during encryption", e)
        card_utils.show_error_dialog(
            f"Error during encryption:\n\n{str(e)}",
            "Encryption Error"
        )
        logger.log_operation_end("Encryption", False, str(e))


def main():
    """Main entry point for the encryption handler"""
    if len(sys.argv) < 2:
        card_utils.show_error_dialog(
            "No file specified for encryption.\n\n"
            "This script should be called from Windows Explorer context menu.",
            "AEPGP Encryption"
        )
        sys.exit(1)

    filepath = sys.argv[1]
    encrypt_file(filepath)


if __name__ == "__main__":
    main()
