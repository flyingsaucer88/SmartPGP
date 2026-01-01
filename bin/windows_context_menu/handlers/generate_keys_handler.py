"""
AEPGP Generate Keys in Card Handler

This script generates RSA key pairs directly on the AEPGP card.
Called from Windows Explorer context menu (no file required).
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import card_utils
from debug_logger import get_logger

# Initialize logger
logger = get_logger()


def generate_keys():
    """
    Generate RSA-2048 key pair on the AEPGP card.

    Uses direct APDU commands to generate keys on the card.
    """
    logger.log_operation_start("Generate Keys", "AEPGP Card")
    logger.log_system_info()

    try:
        # Show confirmation dialog
        confirmed = card_utils.show_question_dialog(
            "This will generate a new RSA-2048 key pair on your AEPGP card.\n\n"
            "WARNING: This will overwrite any existing keys!\n\n"
            "Slot: Decryption/Encryption key\n"
            "Algorithm: RSA-2048\n\n"
            "Do you want to continue?",
            "Generate Keys in Card"
        )

        if not confirmed:
            logger.info("User cancelled key generation")
            logger.log_operation_end("Generate Keys", False, "User cancelled")
            return

        logger.info("Starting key generation on card...")

        # Connect to card
        from card_utils import AEPGPCard
        card = AEPGPCard()

        if not card.connect():
            error_msg = "Failed to connect to AEPGP card"
            logger.error(error_msg)
            card_utils.show_error_dialog(
                "Could not connect to AEPGP card.\n\n"
                "Please ensure:\n"
                "1. The card is inserted\n"
                "2. No other application is using the card",
                "Connection Error"
            )
            logger.log_operation_end("Generate Keys", False, error_msg)
            return

        try:
            logger.info("Connected to card, starting key generation...")

            # Verify admin PIN (required for key generation)
            logger.info("Verifying admin PIN...")
            admin_pin = "12345678"  # Default admin PIN
            pin_bytes = [ord(c) for c in admin_pin]
            verify_apdu = [0x00, 0x20, 0x00, 0x83, len(pin_bytes)] + pin_bytes

            response, sw1, sw2 = card.connection.transmit(verify_apdu)
            card._log_apdu(verify_apdu, response, sw1, sw2)

            if sw1 != 0x90 or sw2 != 0x00:
                error_msg = f"Admin PIN verification failed: SW={sw1:02X}{sw2:02X}"
                logger.error(error_msg)
                card_utils.show_error_dialog(
                    f"Admin PIN verification failed.\n\n"
                    f"Status: {sw1:02X}{sw2:02X}\n\n"
                    f"Make sure you're using the correct admin PIN.\n"
                    f"Default admin PIN: 12345678",
                    "PIN Verification Error"
                )
                logger.log_operation_end("Generate Keys", False, error_msg)
                card.disconnect()
                return

            logger.info("Admin PIN verified")

            # Show progress dialog
            card_utils.show_info_dialog(
                "Generating RSA-2048 key pair on card...\n\n"
                "This may take 30-60 seconds.\n"
                "Please wait and do not remove the card...",
                "Generating Keys"
            )

            # Generate key pair for decryption slot (0xB8)
            logger.info("Generating RSA-2048 key pair (this may take up to 60 seconds)...")

            # APDU: 00 47 80 00 02 B8 00 00
            # CLA=00, INS=47, P1=80 (generate), P2=00
            # Data: B8 00 (decryption slot + empty template)
            # Le=00 (expect response)
            gen_apdu = [0x00, 0x47, 0x80, 0x00, 0x02, 0xB8, 0x00, 0x00]

            response, sw1, sw2 = card.connection.transmit(gen_apdu)
            card._log_apdu(gen_apdu, response, sw1, sw2)

            # Handle GET RESPONSE if needed (SW=61XX means more data available)
            if sw1 == 0x61:
                logger.info(f"Fetching remaining {sw2} bytes with GET RESPONSE...")
                get_response = [0x00, 0xC0, 0x00, 0x00, sw2]
                response2, sw1, sw2 = card.connection.transmit(get_response)
                card._log_apdu(get_response, response2, sw1, sw2)
                response = response + response2

            # Check if generation was successful
            if sw1 != 0x90 or sw2 != 0x00:
                error_msg = f"Key generation failed: SW={sw1:02X}{sw2:02X}"
                logger.error(error_msg)
                card_utils.show_error_dialog(
                    f"Key generation failed.\n\n"
                    f"Status: {sw1:02X}{sw2:02X}\n\n"
                    f"Please try again. If the problem persists,\n"
                    f"try resetting the card.",
                    "Key Generation Error"
                )
                logger.log_operation_end("Generate Keys", False, error_msg)
                card.disconnect()
                return

            logger.info(f"Key generation successful! Generated {len(response)} bytes of public key data")

            # Verify the key can be read
            logger.info("Verifying generated key...")
            read_apdu = [0x00, 0x47, 0x81, 0x00, 0x02, 0xB8, 0x00, 0x00]
            response, sw1, sw2 = card.connection.transmit(read_apdu)
            card._log_apdu(read_apdu, response, sw1, sw2)

            if sw1 == 0x90 or sw1 == 0x61:
                logger.info("Key verification successful!")
            else:
                logger.warning(f"Key verification returned SW={sw1:02X}{sw2:02X}, but generation reported success")

            # Success!
            card_utils.show_info_dialog(
                "RSA-2048 key pair generated successfully!\n\n"
                "Slot: Decryption/Encryption\n"
                "Algorithm: RSA-2048\n\n"
                "The key pair is now stored securely on your AEPGP card.\n"
                "The private key will never leave the card.\n\n"
                "You can now use this key for encryption and decryption.",
                "Key Generation Successful"
            )
            logger.log_operation_end("Generate Keys", True)

        finally:
            card.disconnect()

    except Exception as e:
        logger.error("Exception during key generation", e)
        import traceback
        logger.error(traceback.format_exc())
        card_utils.show_error_dialog(
            f"Error during key generation:\n\n{str(e)}",
            "Key Generation Error"
        )
        logger.log_operation_end("Generate Keys", False, str(e))


def main():
    """Main entry point for the key generation handler"""
    generate_keys()


if __name__ == "__main__":
    main()
