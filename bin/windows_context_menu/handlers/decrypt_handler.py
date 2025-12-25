"""
AEPGP File Decryption Handler

This script is called when the user right-clicks an encrypted file (.gpg, .pgp)
and selects "Decrypt with AEPGP" from the context menu.
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


def decrypt_file(filepath):
    """
    Decrypt a file using GnuPG with the AEPGP card.

    Args:
        filepath: Path to the encrypted file to decrypt
    """
    # Verify file exists
    if not os.path.exists(filepath):
        card_utils.show_error_dialog(
            f"File not found:\n{filepath}",
            "AEPGP Decryption Error"
        )
        return

    # Check file extension
    if not (filepath.endswith('.gpg') or filepath.endswith('.pgp') or filepath.endswith('.asc')):
        card_utils.show_error_dialog(
            "This file does not appear to be encrypted.\n\n"
            "Encrypted files typically have .gpg, .pgp, or .asc extensions.",
            "Invalid File Type"
        )
        return

    # Check for AEPGP card
    card, error = card_utils.find_aepgp_card()
    if error:
        card_utils.show_error_dialog(
            f"Cannot decrypt file:\n\n{error}",
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

    # Prepare output filename (remove .gpg/.pgp extension)
    if filepath.endswith('.gpg'):
        output_path = filepath[:-4]
    elif filepath.endswith('.pgp'):
        output_path = filepath[:-4]
    elif filepath.endswith('.asc'):
        output_path = filepath[:-4]
    else:
        output_path = filepath + ".decrypted"

    # Check if output file already exists
    if os.path.exists(output_path):
        overwrite = card_utils.show_question_dialog(
            f"The decrypted file already exists:\n\n{output_path}\n\n"
            "Do you want to overwrite it?",
            "File Already Exists"
        )
        if not overwrite:
            return

    try:
        # Build GPG command
        cmd = [
            gpg_path,
            "--output", output_path,
            "--decrypt",
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
                f"File decrypted successfully!\n\n"
                f"Encrypted: {os.path.basename(filepath)}\n"
                f"Decrypted: {os.path.basename(output_path)}\n\n"
                f"Location: {os.path.dirname(output_path)}",
                "Decryption Successful"
            )
        else:
            # Decryption failed
            error_msg = result.stderr if result.stderr else "Unknown error"
            card_utils.show_error_dialog(
                f"Decryption failed:\n\n{error_msg}\n\n"
                "Make sure:\n"
                "1. Your AEPGP card is inserted\n"
                "2. You enter the correct PIN\n"
                "3. The file was encrypted for your key",
                "Decryption Error"
            )

    except Exception as e:
        card_utils.show_error_dialog(
            f"Error during decryption:\n\n{str(e)}",
            "Decryption Error"
        )


def main():
    """Main entry point for the decryption handler"""
    if len(sys.argv) < 2:
        card_utils.show_error_dialog(
            "No file specified for decryption.\n\n"
            "This script should be called from Windows Explorer context menu.",
            "AEPGP Decryption"
        )
        sys.exit(1)

    filepath = sys.argv[1]
    decrypt_file(filepath)


if __name__ == "__main__":
    main()
