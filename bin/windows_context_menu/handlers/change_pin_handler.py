"""
AEPGP Change PIN Handler

This script changes the user PIN on the AEPGP card.
Called from Windows Explorer context menu (Desktop background).
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import card_utils
from debug_logger import get_logger

# Initialize logger
logger = get_logger()


def change_pin():
    """
    Change the PIN on the AEPGP card.

    Prompts for current PIN and new PIN, then updates the card.
    """
    logger.log_operation_start("Change PIN", "AEPGP Card")
    logger.log_system_info()

    try:
        import tkinter as tk
        from tkinter import simpledialog, messagebox

        # Create root window
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        # Show info dialog
        card_utils.show_info_dialog(
            "This will change the PIN on your AEPGP card.\n\n"
            "You will need to enter:\n"
            "1. Your current PIN\n"
            "2. Your new PIN (twice for confirmation)",
            "Change AEPGP Card PIN"
        )

        # Prompt for current PIN
        logger.info("Prompting for current PIN...")
        current_pin = simpledialog.askstring(
            "Current PIN",
            "Enter your current AEPGP card PIN:",
            show='*',
            parent=root
        )

        if current_pin is None or current_pin == "":
            logger.info("User cancelled current PIN entry")
            logger.log_operation_end("Change PIN", False, "User cancelled")
            root.destroy()
            return

        # Prompt for new PIN
        logger.info("Prompting for new PIN...")
        new_pin = simpledialog.askstring(
            "New PIN",
            "Enter your new PIN:\n(6-8 digits recommended)",
            show='*',
            parent=root
        )

        if new_pin is None or new_pin == "":
            logger.info("User cancelled new PIN entry")
            logger.log_operation_end("Change PIN", False, "User cancelled")
            root.destroy()
            return

        # Confirm new PIN
        logger.info("Prompting for new PIN confirmation...")
        confirm_pin = simpledialog.askstring(
            "Confirm New PIN",
            "Re-enter your new PIN to confirm:",
            show='*',
            parent=root
        )

        root.destroy()

        if confirm_pin is None or confirm_pin == "":
            logger.info("User cancelled PIN confirmation")
            logger.log_operation_end("Change PIN", False, "User cancelled")
            return

        # Verify new PIN matches confirmation
        if new_pin != confirm_pin:
            error_msg = "New PIN and confirmation do not match"
            logger.error(error_msg)
            card_utils.show_error_dialog(
                "The new PIN and confirmation PIN do not match.\n\n"
                "Please try again.",
                "PIN Mismatch"
            )
            logger.log_operation_end("Change PIN", False, error_msg)
            return

        # Validate PIN length (OpenPGP spec: 6-127 bytes)
        if len(new_pin) < 6:
            error_msg = f"New PIN too short: {len(new_pin)} characters (minimum 6)"
            logger.error(error_msg)
            card_utils.show_error_dialog(
                f"New PIN is too short ({len(new_pin)} characters).\n\n"
                "Minimum length: 6 characters\n"
                "Recommended: 6-8 digits",
                "Invalid PIN Length"
            )
            logger.log_operation_end("Change PIN", False, error_msg)
            return

        if len(new_pin) > 127:
            error_msg = f"New PIN too long: {len(new_pin)} characters (maximum 127)"
            logger.error(error_msg)
            card_utils.show_error_dialog(
                f"New PIN is too long ({len(new_pin)} characters).\n\n"
                "Maximum length: 127 characters",
                "Invalid PIN Length"
            )
            logger.log_operation_end("Change PIN", False, error_msg)
            return

        # Connect to card
        logger.info("Connecting to AEPGP card...")
        from card_utils import find_aepgp_card

        card, error = find_aepgp_card()
        if error:
            error_msg = f"Card not found: {error}"
            logger.error(error_msg)
            card_utils.show_error_dialog(
                f"AEPGP card not found:\n\n{error}\n\n"
                "Please insert your AEPGP card and try again.",
                "Card Not Found"
            )
            logger.log_operation_end("Change PIN", False, error_msg)
            return

        logger.info(f"Card found: {card.reader}")

        try:
            # Select OpenPGP applet
            card.select_applet()

            # Verify current PIN first
            logger.info("Verifying current PIN...")
            current_pin_bytes = [ord(c) for c in current_pin]
            verify_pin_cmd = [0x00, 0x20, 0x00, 0x82, len(current_pin_bytes)] + current_pin_bytes

            response, sw1, sw2 = card.connection.transmit(verify_pin_cmd)
            card._log_apdu(verify_pin_cmd, response, sw1, sw2)

            if sw1 == 0x90 and sw2 == 0x00:
                logger.info("Current PIN verified successfully")
            elif sw1 == 0x63:
                retries = sw2 & 0x0F
                error_msg = f"Wrong current PIN. {retries} retries remaining"
                logger.error(error_msg)
                card_utils.show_error_dialog(
                    f"Incorrect current PIN.\n\n"
                    f"{retries} attempts remaining before card is locked.\n\n"
                    "Please try again with the correct PIN.",
                    "PIN Verification Failed"
                )
                logger.log_operation_end("Change PIN", False, error_msg)
                return
            else:
                error_msg = f"PIN verification failed: SW={sw1:02X}{sw2:02X}"
                logger.error(error_msg)
                card_utils.show_error_dialog(
                    f"PIN verification failed.\n\n"
                    f"Error code: {sw1:02X}{sw2:02X}",
                    "Verification Error"
                )
                logger.log_operation_end("Change PIN", False, error_msg)
                return

            # Disconnect from card before using GPG
            card.disconnect()
            logger.debug("Card disconnected before GPG operation")

            # Change PIN using GPG passwd command (most reliable method)
            logger.info("Changing PIN using GPG passwd command...")

            import subprocess
            import time

            try:
                # Create automated input for gpg
                gpg_input = f"{current_pin}\n{new_pin}\n{new_pin}\n"
                gpg_commands = f"admin\npasswd\n1\n{gpg_input}quit\n"

                logger.debug("Executing GPG PIN change command")
                result = subprocess.run(
                    "gpg --command-fd 0 --status-fd 2 --card-edit",
                    input=gpg_commands,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                logger.debug(f"GPG command completed with return code: {result.returncode}")

                # Kill GPG agent to release card
                logger.info("Terminating GPG agent...")
                subprocess.run("gpgconf --kill scdaemon", shell=True, capture_output=True, timeout=5)
                subprocess.run("gpgconf --kill gpg-agent", shell=True, capture_output=True, timeout=5)
                time.sleep(1)

            except Exception as e:
                logger.error(f"GPG command error: {e}")
                # Continue to verification

            # Reconnect and verify new PIN
            logger.info("Verifying PIN change...")
            card, error = find_aepgp_card()
            if error:
                error_msg = f"Cannot reconnect to card: {error}"
                logger.error(error_msg)
                card_utils.show_error_dialog(
                    f"PIN may have changed, but cannot verify:\n\n{error}",
                    "Verification Warning"
                )
                logger.log_operation_end("Change PIN", False, error_msg)
                return

            card.select_applet()

            # Verify new PIN works
            new_pin_bytes = [ord(c) for c in new_pin]
            verify_new_cmd = [0x00, 0x20, 0x00, 0x82, len(new_pin_bytes)] + new_pin_bytes
            response, sw1, sw2 = card.connection.transmit(verify_new_cmd)
            card._log_apdu(verify_new_cmd, response, sw1, sw2)

            if sw1 == 0x90 and sw2 == 0x00:
                logger.info("PIN changed successfully!")
                card_utils.show_info_dialog(
                    "PIN changed successfully!\n\n"
                    "Your new PIN has been set on the AEPGP card.\n\n"
                    "Please remember your new PIN.",
                    "PIN Change Successful"
                )
                logger.log_operation_end("Change PIN", True)
            else:
                error_msg = f"New PIN verification failed: SW={sw1:02X}{sw2:02X}"
                logger.error(error_msg)
                card_utils.show_error_dialog(
                    f"PIN change may have failed.\n\n"
                    f"Verification error: {sw1:02X}{sw2:02X}\n\n"
                    "Your PIN may still be the old PIN.",
                    "PIN Change Failed"
                )
                logger.log_operation_end("Change PIN", False, error_msg)

        finally:
            card.disconnect()
            logger.debug("Card disconnected")

    except Exception as e:
        logger.error("Exception during PIN change", e)
        import traceback
        logger.error(traceback.format_exc())
        card_utils.show_error_dialog(
            f"Error during PIN change:\n\n{str(e)}",
            "PIN Change Error"
        )
        logger.log_operation_end("Change PIN", False, str(e))


def main():
    """Main entry point for the PIN change handler"""
    change_pin()


if __name__ == "__main__":
    main()
