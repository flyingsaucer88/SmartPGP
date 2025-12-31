"""
AEPGP Delete Keys Handler

This script deletes all keys from the AEPGP card (factory reset).
Called from Windows Explorer context menu.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import card_utils
from debug_logger import get_logger

# Initialize logger
logger = get_logger()


def delete_keys():
    """
    Delete all keys from the AEPGP card (factory reset).

    WARNING: This operation is irreversible!
    """
    logger.log_operation_start("Delete Keys", "AEPGP Card")
    logger.log_system_info()

    try:
        import tkinter as tk
        from tkinter import simpledialog, messagebox

        # Create root window
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        # Verify PIN first
        logger.info("Prompting for PIN verification...")
        pin = simpledialog.askstring(
            "PIN Verification",
            "Enter your AEPGP card PIN to continue:",
            show='*',
            parent=root
        )

        if pin is None or pin == "":
            logger.info("User cancelled PIN entry")
            logger.log_operation_end("Delete Keys", False, "User cancelled")
            root.destroy()
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
            logger.log_operation_end("Delete Keys", False, error_msg)
            root.destroy()
            return

        logger.info(f"Card found: {card.reader}")

        try:
            # Select OpenPGP applet
            card.select_applet()

            # Verify PIN
            logger.info("Verifying PIN...")
            pin_bytes = [ord(c) for c in pin]
            verify_pin_cmd = [0x00, 0x20, 0x00, 0x82, len(pin_bytes)] + pin_bytes

            response, sw1, sw2 = card.connection.transmit(verify_pin_cmd)
            card._log_apdu(verify_pin_cmd, response, sw1, sw2)

            if sw1 == 0x90 and sw2 == 0x00:
                logger.info("PIN verified successfully")
            elif sw1 == 0x63:
                retries = sw2 & 0x0F
                error_msg = f"Wrong PIN. {retries} retries remaining"
                logger.error(error_msg)
                card_utils.show_error_dialog(
                    f"Incorrect PIN.\n\n"
                    f"{retries} attempts remaining before card is locked.\n\n"
                    "Please try again with the correct PIN.",
                    "PIN Verification Failed"
                )
                logger.log_operation_end("Delete Keys", False, error_msg)
                root.destroy()
                return
            else:
                error_msg = f"PIN verification failed: SW={sw1:02X}{sw2:02X}"
                logger.error(error_msg)
                card_utils.show_error_dialog(
                    f"PIN verification failed.\n\n"
                    f"Error code: {sw1:02X}{sw2:02X}",
                    "Verification Error"
                )
                logger.log_operation_end("Delete Keys", False, error_msg)
                root.destroy()
                return

            # Final confirmation
            result = messagebox.askyesno(
                "Confirm Delete Keys",
                "WARNING: This will delete ALL keys from your AEPGP card!\n\n"
                "This operation is IRREVERSIBLE.\n\n"
                "Are you sure you want to continue?",
                icon='warning',
                parent=root
            )

            if not result:
                logger.info("User cancelled key deletion")
                logger.log_operation_end("Delete Keys", False, "User cancelled")
                root.destroy()
                return

            # Disconnect from card before using GPG
            card.disconnect()
            logger.debug("Card disconnected before GPG operation")

            # Perform factory reset using GPG
            logger.info("Performing factory reset...")

            import subprocess
            import time

            try:
                # Create automated input for gpg factory-reset
                # Sequence: admin → factory-reset → yes → yes
                gpg_commands = "admin\nfactory-reset\nyes\nyes\nquit\n"

                logger.debug("Executing GPG factory reset command")
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

                # Success message
                logger.info("Keys deleted successfully!")
                card_utils.show_info_dialog(
                    "All keys have been deleted from your AEPGP card.\n\n"
                    "The card has been reset to factory defaults.\n\n"
                    "Default PIN: 123456\n"
                    "Default Admin PIN: 12345678",
                    "Keys Deleted Successfully"
                )
                logger.log_operation_end("Delete Keys", True)

            except Exception as e:
                error_msg = f"GPG command error: {e}"
                logger.error(error_msg)
                card_utils.show_error_dialog(
                    f"Error during key deletion:\n\n{str(e)}",
                    "Delete Keys Error"
                )
                logger.log_operation_end("Delete Keys", False, error_msg)

        finally:
            try:
                card.disconnect()
                logger.debug("Card disconnected")
            except:
                pass

        root.destroy()

    except Exception as e:
        logger.error("Exception during key deletion", e)
        import traceback
        logger.error(traceback.format_exc())
        card_utils.show_error_dialog(
            f"Error during key deletion:\n\n{str(e)}",
            "Delete Keys Error"
        )
        logger.log_operation_end("Delete Keys", False, str(e))


def main():
    """Main entry point for the delete keys handler"""
    delete_keys()


if __name__ == "__main__":
    main()
