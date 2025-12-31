"""
AEPGP Import PFX to Card Handler

This script imports an RSA private key from a PFX file to the AEPGP card.
Called from Windows Explorer context menu when right-clicking a .pfx file.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import card_utils
from debug_logger import get_logger

# Initialize logger
logger = get_logger()


def import_pfx_to_card(pfx_file):
    """
    Import RSA private key from PFX file to AEPGP card.

    Args:
        pfx_file: Path to the .pfx file
    """
    logger.log_operation_start("Import PFX to Card", pfx_file)
    logger.log_system_info()

    # Verify file exists
    if not os.path.exists(pfx_file):
        logger.error(f"PFX file not found: {pfx_file}")
        card_utils.show_error_dialog(
            f"PFX file not found:\n{pfx_file}",
            "Import PFX Error"
        )
        logger.log_operation_end("Import PFX", False, "File not found")
        return

    logger.info(f"PFX file exists, size: {os.path.getsize(pfx_file)} bytes")

    try:
        from cryptography.hazmat.primitives.serialization import pkcs12, Encoding, PrivateFormat, NoEncryption
        from cryptography.hazmat.backends import default_backend
        import tkinter as tk
        from tkinter import simpledialog

        # Ask for PFX password
        logger.info("Prompting for PFX password...")
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        root.attributes('-topmost', True)  # Make dialog appear on top

        password = simpledialog.askstring(
            "PFX Password",
            f"Enter password for PFX file:\n{os.path.basename(pfx_file)}",
            show='*',
            parent=root
        )

        root.destroy()

        if password is None:
            logger.info("User cancelled password entry")
            logger.log_operation_end("Import PFX", False, "User cancelled")
            return

        # Read and parse PFX file
        logger.info("Reading PFX file...")
        with open(pfx_file, 'rb') as f:
            pfx_data = f.read()

        logger.info("Parsing PFX file...")
        try:
            password_bytes = password.encode('utf-8') if password else None
            private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
                pfx_data,
                password_bytes,
                backend=default_backend()
            )
        except Exception as e:
            error_msg = f"Failed to parse PFX file: {str(e)}"
            logger.error(error_msg)
            if "password" in str(e).lower() or "mac" in str(e).lower():
                card_utils.show_error_dialog(
                    "Incorrect password for PFX file.\n\n"
                    "Please try again with the correct password.",
                    "Invalid Password"
                )
            else:
                card_utils.show_error_dialog(
                    f"Failed to parse PFX file:\n\n{str(e)}",
                    "PFX Parse Error"
                )
            logger.log_operation_end("Import PFX", False, error_msg)
            return

        if private_key is None:
            error_msg = "No private key found in PFX file"
            logger.error(error_msg)
            card_utils.show_error_dialog(
                "No private key found in the PFX file.\n\n"
                "Please ensure the PFX file contains a private key.",
                "No Private Key"
            )
            logger.log_operation_end("Import PFX", False, error_msg)
            return

        # Check if it's an RSA key
        from cryptography.hazmat.primitives.asymmetric import rsa
        if not isinstance(private_key, rsa.RSAPrivateKey):
            error_msg = f"Unsupported key type: {type(private_key).__name__}"
            logger.error(error_msg)
            card_utils.show_error_dialog(
                f"Unsupported key type: {type(private_key).__name__}\n\n"
                "Only RSA keys are supported.",
                "Unsupported Key Type"
            )
            logger.log_operation_end("Import PFX", False, error_msg)
            return

        # Get key size
        key_size = private_key.key_size
        logger.info(f"Found RSA private key: {key_size} bits")

        if key_size != 2048:
            error_msg = f"Unsupported key size: {key_size} bits (only 2048-bit RSA supported)"
            logger.error(error_msg)
            card_utils.show_error_dialog(
                f"Unsupported key size: {key_size} bits\n\n"
                "AEPGP cards support only RSA-2048.\n"
                "Please use a 2048-bit RSA key.",
                "Unsupported Key Size"
            )
            logger.log_operation_end("Import PFX", False, error_msg)
            return

        # Show certificate info if available
        cert_info = ""
        if certificate:
            subject = certificate.subject.rfc4514_string()
            cert_info = f"\n\nCertificate Subject:\n{subject}"
            logger.info(f"Certificate found: {subject}")

        # Confirm import
        confirmed = card_utils.show_question_dialog(
            f"Found RSA-2048 private key in PFX file.{cert_info}\n\n"
            "WARNING: This will overwrite the decryption key on your AEPGP card!\n\n"
            "The private key will be securely imported to the card.\n"
            "After import, the private key will never leave the card.\n\n"
            "Do you want to continue?",
            "Confirm PFX Import"
        )

        if not confirmed:
            logger.info("User cancelled PFX import")
            logger.log_operation_end("Import PFX", False, "User cancelled")
            return

        # Import private key to card
        logger.info("Importing private key to AEPGP card...")

        # Extract RSA key components
        from cryptography.hazmat.primitives.asymmetric import rsa
        private_numbers = private_key.private_numbers()
        public_numbers = private_numbers.public_numbers

        # Get components (all in big-endian format)
        e = public_numbers.e.to_bytes(4, 'big')  # Public exponent (usually 65537, 4 bytes)
        n = public_numbers.n.to_bytes(256, 'big')  # Modulus (256 bytes for RSA-2048)
        p = private_numbers.p.to_bytes(128, 'big')  # Prime p (128 bytes)
        q = private_numbers.q.to_bytes(128, 'big')  # Prime q (128 bytes)
        d = private_numbers.d

        # Calculate CRT parameters
        dp = private_numbers.dmp1.to_bytes(128, 'big')  # d mod (p-1)
        dq = private_numbers.dmq1.to_bytes(128, 'big')  # d mod (q-1)
        qinv = private_numbers.iqmp.to_bytes(128, 'big')  # q^-1 mod p

        logger.info(f"Extracted RSA components: e={len(e)} bytes, n={len(n)} bytes, p={len(p)} bytes")

        # Connect to card
        logger.info("Connecting to AEPGP card...")
        card, error = card_utils.find_aepgp_card()
        if error:
            error_msg = f"Card not found: {error}"
            logger.error(error_msg)
            card_utils.show_error_dialog(
                f"AEPGP card not found:\n\n{error}\n\n"
                "Please insert your AEPGP card and try again.",
                "Card Not Found"
            )
            logger.log_operation_end("Import PFX", False, error_msg)
            return

        logger.info(f"Card found: {card.reader}")

        try:
            # Select OpenPGP applet
            card.select_applet()

            # Get admin PIN from user
            logger.info("Prompting for admin PIN...")
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)

            admin_pin = simpledialog.askstring(
                "Admin PIN Required",
                "Enter your AEPGP card Admin PIN:\n(Default: 12345678)",
                show='*',
                parent=root
            )
            root.destroy()

            if admin_pin is None or admin_pin == "":
                logger.info("User cancelled admin PIN entry")
                logger.log_operation_end("Import PFX", False, "User cancelled")
                card.disconnect()
                return

            # Build PUT DATA APDU for RSA key import
            # Format: 4D <len> B8 <len> 7F48 <template> 5F48 <data>
            logger.info("Building key import APDU...")

            # Build Private Key Template (7F48)
            template = []
            # Tag 91: Public exponent (4 bytes)
            template.extend([0x91, len(e)] + list(e))
            # Tag 92: Prime p (128 bytes)
            template.extend([0x92, 0x81, len(p)] + list(p))
            # Tag 93: Prime q (128 bytes)
            template.extend([0x93, 0x81, len(q)] + list(q))
            # Tag 94: PQ (qinv) (128 bytes)
            template.extend([0x94, 0x81, len(qinv)] + list(qinv))
            # Tag 95: DP1 (dp) (128 bytes)
            template.extend([0x95, 0x81, len(dp)] + list(dp))
            # Tag 96: DQ1 (dq) (128 bytes)
            template.extend([0x96, 0x81, len(dq)] + list(dq))
            # Tag 97: Modulus n (256 bytes)
            template.extend([0x97, 0x82, 0x01, 0x00] + list(n))

            # Build Concatenated Data (5F48)
            concat_data = list(e) + list(p) + list(q) + list(qinv) + list(dp) + list(dq) + list(n)

            # Build Extended Header (4D)
            extended_header = [0xB8]  # Decryption key tag
            # 7F48 template
            template_with_tag = [0x7F, 0x48, 0x82] + list(len(template).to_bytes(2, 'big')) + template
            # 5F48 data
            data_with_tag = [0x5F, 0x48, 0x82] + list(len(concat_data).to_bytes(2, 'big')) + concat_data

            extended_content = extended_header + template_with_tag + data_with_tag

            # Final APDU data
            apdu_data = [0x4D, 0x82] + list(len(extended_content).to_bytes(2, 'big')) + extended_content

            logger.info(f"APDU data size: {len(apdu_data)} bytes")

            # Verify admin PIN right before sending data
            logger.info("Verifying admin PIN before key import...")
            pin_bytes = [ord(c) for c in admin_pin]
            verify_pin_cmd = [0x00, 0x20, 0x00, 0x83, len(pin_bytes)] + pin_bytes

            response, sw1, sw2 = card.connection.transmit(verify_pin_cmd)
            card._log_apdu(verify_pin_cmd, response, sw1, sw2)

            if sw1 == 0x90 and sw2 == 0x00:
                logger.info("Admin PIN verified successfully")
            elif sw1 == 0x63:
                retries = sw2 & 0x0F
                error_msg = f"Wrong admin PIN. {retries} retries remaining"
                logger.error(error_msg)
                card_utils.show_error_dialog(
                    f"Incorrect Admin PIN.\n\n"
                    f"{retries} attempts remaining before card is locked.\n\n"
                    "Please try again with the correct Admin PIN.",
                    "Admin PIN Verification Failed"
                )
                logger.log_operation_end("Import PFX", False, error_msg)
                card.disconnect()
                return
            else:
                error_msg = f"Admin PIN verification failed: SW={sw1:02X}{sw2:02X}"
                logger.error(error_msg)
                card_utils.show_error_dialog(
                    f"Admin PIN verification failed.\n\n"
                    f"Error code: {sw1:02X}{sw2:02X}",
                    "Verification Error"
                )
                logger.log_operation_end("Import PFX", False, error_msg)
                card.disconnect()
                return

            # Send PUT DATA command using larger chunks to minimize security timeout issues
            # Security state expires after ~620ms, so we need to send fewer chunks
            # Try 512 bytes per chunk instead of 255
            MAX_CHUNK_SIZE = 512  # Larger chunks = fewer total chunks = faster completion

            offset = 0
            chunk_num = 0
            total_chunks = (len(apdu_data) + MAX_CHUNK_SIZE - 1) // MAX_CHUNK_SIZE

            logger.info(f"Sending key import in {total_chunks} chunks (max {MAX_CHUNK_SIZE} bytes each)...")

            while offset < len(apdu_data):
                chunk_size = min(MAX_CHUNK_SIZE, len(apdu_data) - offset)
                chunk_data = apdu_data[offset:offset + chunk_size]

                # Use CLA=0x10 for all chunks except the last one (CLA=0x00)
                is_last_chunk = (offset + chunk_size >= len(apdu_data))
                cla = 0x00 if is_last_chunk else 0x10

                # APDU: CLA INS P1 P2 Lc Data
                # For chunks > 255 bytes, use extended length encoding (3 bytes)
                if chunk_size > 255:
                    lc_bytes = [0x00, (chunk_size >> 8) & 0xFF, chunk_size & 0xFF]
                else:
                    lc_bytes = [chunk_size]

                put_data_cmd = [cla, 0xDB, 0x3F, 0xFF] + lc_bytes + chunk_data

                chunk_num += 1
                logger.info(f"Sending chunk {chunk_num}/{total_chunks} ({chunk_size} bytes)...")
                response, sw1, sw2 = card.connection.transmit(put_data_cmd)
                card._log_apdu(put_data_cmd, response, sw1, sw2)

                # Check response - should return 0x90 0x00
                if sw1 != 0x90 or sw2 != 0x00:
                    error_msg = f"Chunk {chunk_num} failed: SW={sw1:02X}{sw2:02X}"
                    logger.error(error_msg)
                    card_utils.show_error_dialog(
                        f"Failed to send data chunk {chunk_num}/{total_chunks}.\n\n"
                        f"Error code: {sw1:02X}{sw2:02X}\n\n"
                        "The key was not imported.",
                        "Import Failed"
                    )
                    logger.log_operation_end("Import PFX", False, error_msg)
                    # Clear admin PIN from memory
                    admin_pin = None
                    card.disconnect()
                    return

                offset += chunk_size

            # Clear admin PIN from memory immediately after import
            admin_pin = None
            pin_bytes = None

            # Check final response
            if sw1 == 0x90 and sw2 == 0x00:
                logger.info("Private key imported successfully!")
                card_utils.show_info_dialog(
                    "Private key imported successfully!\n\n"
                    "The RSA-2048 private key from your PFX file has been\n"
                    "securely imported to the AEPGP card decryption key slot.\n\n"
                    "The private key will never leave the card.",
                    "Import Successful"
                )
                logger.log_operation_end("Import PFX", True)
            else:
                error_msg = f"Key import failed: SW={sw1:02X}{sw2:02X}"
                logger.error(error_msg)
                card_utils.show_error_dialog(
                    f"Failed to import private key to card.\n\n"
                    f"Error code: {sw1:02X}{sw2:02X}\n\n"
                    "The key was not imported.",
                    "Import Failed"
                )
                logger.log_operation_end("Import PFX", False, error_msg)

        finally:
            try:
                card.disconnect()
                logger.debug("Card disconnected")
            except:
                pass

    except ImportError as e:
        error_msg = f"Missing required module: {str(e)}"
        logger.error(error_msg)
        card_utils.show_error_dialog(
            f"Missing required module:\n\n{str(e)}\n\n"
            "Please install: pip install cryptography",
            "Module Not Found"
        )
        logger.log_operation_end("Import PFX", False, error_msg)

    except Exception as e:
        logger.error("Exception during PFX import", e)
        import traceback
        logger.error(traceback.format_exc())
        card_utils.show_error_dialog(
            f"Error during PFX import:\n\n{str(e)}",
            "PFX Import Error"
        )
        logger.log_operation_end("Import PFX", False, str(e))


def main():
    """Main entry point for the PFX import handler"""
    if len(sys.argv) < 2:
        card_utils.show_error_dialog(
            "No PFX file specified.\n\n"
            "This script should be called from Windows Explorer context menu.",
            "Import PFX to Card"
        )
        sys.exit(1)

    pfx_file = sys.argv[1]
    import_pfx_to_card(pfx_file)


if __name__ == "__main__":
    main()
