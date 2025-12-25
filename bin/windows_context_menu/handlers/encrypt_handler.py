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
    # Verify file exists
    if not os.path.exists(filepath):
        card_utils.show_error_dialog(
            f"File not found:\n{filepath}",
            "AEPGP Encryption Error"
        )
        return

    # Check for AEPGP card
    card, error = card_utils.find_aepgp_card()
    if error:
        card_utils.show_error_dialog(
            f"Cannot encrypt file:\n\n{error}",
            "AEPGP Card Not Found"
        )
        return

    # Card found, disconnect as GPG will handle the connection
    card.disconnect()

    # Find GnuPG
    gpg_path = find_gpg_executable()
    if not gpg_path:
        card_utils.show_error_dialog(
            "GnuPG (gpg.exe) not found on your system.\n\n"
            "Please install GnuPG from:\n"
            "https://www.gnupg.org/download/\n\n"
            "Or install Gpg4win from:\n"
            "https://www.gpg4win.org/",
            "GnuPG Not Found"
        )
        return

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

        # Run GPG (this will prompt for PIN via pinentry)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )

        if result.returncode == 0:
            # Success!
            card_utils.show_info_dialog(
                f"File encrypted successfully!\n\n"
                f"Original: {os.path.basename(filepath)}\n"
                f"Encrypted: {os.path.basename(output_path)}\n\n"
                f"Location: {os.path.dirname(output_path)}",
                "Encryption Successful"
            )
        else:
            # Encryption failed
            error_msg = result.stderr if result.stderr else "Unknown error"
            card_utils.show_error_dialog(
                f"Encryption failed:\n\n{error_msg}",
                "Encryption Error"
            )

    except Exception as e:
        card_utils.show_error_dialog(
            f"Error during encryption:\n\n{str(e)}",
            "Encryption Error"
        )


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
