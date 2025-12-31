"""
AEPGP RSA Encryption Module

This module provides RSA encryption using the AEPGP card's public key.
Uses the cryptography library for hybrid encryption (RSA + AES).
"""

import os
import sys
from pathlib import Path

# Import debug logger
try:
    from debug_logger import get_logger
    logger = get_logger()
except ImportError:
    class DummyLogger:
        def info(self, msg): print(f"INFO: {msg}")
        def error(self, msg, e=None): print(f"ERROR: {msg}")
        def debug(self, msg): print(f"DEBUG: {msg}")
    logger = DummyLogger()

try:
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    logger.info("Cryptography library imported successfully")
except ImportError:
    logger.error("Cryptography library not found. Install it with: pip install cryptography")
    print("ERROR: Cryptography library not found.")
    sys.exit(1)


def encrypt_file_with_card_key(input_file, output_file):
    """
    Encrypt a file using hybrid encryption (RSA + AES) with the card's public key.

    Uses AES-256-GCM for file encryption and RSA-OAEP for key encryption.

    Args:
        input_file: Path to file to encrypt
        output_file: Path for encrypted output

    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    try:
        from card_utils import find_aepgp_card
        from card_key_reader import read_public_key_from_card, extract_rsa_public_key_components
        import struct

        logger.info(f"Starting file encryption: {input_file}")
        print(f"Encrypting: {input_file}")

        # Read the input file
        if not os.path.exists(input_file):
            error_msg = f"Input file not found: {input_file}"
            logger.error(error_msg)
            return False, error_msg

        logger.debug(f"Reading input file...")
        with open(input_file, 'rb') as f:
            plaintext = f.read()
        logger.info(f"Read {len(plaintext)} bytes from input file")
        print(f"File size: {len(plaintext)} bytes")

        # Find and connect to card
        logger.info("Connecting to AEPGP card...")
        print("Connecting to AEPGP card...")
        card, error = find_aepgp_card()
        if error:
            error_msg = f"Card not found: {error}"
            logger.error(error_msg)
            return False, error_msg

        logger.info(f"Card found: {card.reader}")
        print(f"Card found: {card.reader}")

        try:
            # Select OpenPGP applet
            card.select_applet()

            # Read public key from card
            logger.info("Reading public key from card...")
            print("Reading public key from card...")
            key_data = read_public_key_from_card(card, 'encryption')
            if not key_data:
                error_msg = "Failed to read public key from card"
                logger.error(error_msg)
                return False, error_msg

            # Extract RSA components
            modulus_bytes, exponent_bytes = extract_rsa_public_key_components(key_data)
            if not modulus_bytes or not exponent_bytes:
                error_msg = "Failed to extract RSA components"
                logger.error(error_msg)
                return False, error_msg

            # Create RSA public key
            n = int.from_bytes(modulus_bytes, byteorder='big')
            e = int.from_bytes(exponent_bytes, byteorder='big')
            public_numbers = rsa.RSAPublicNumbers(e, n)
            rsa_public_key = public_numbers.public_key(default_backend())

            logger.info(f"Successfully loaded RSA public key: {n.bit_length()} bits")
            print(f"Public key loaded: {n.bit_length()} bits")

        finally:
            card.disconnect()
            logger.debug("Card disconnected")

        # Generate random AES key and IV
        logger.debug("Generating AES key and IV...")
        aes_key = os.urandom(32)  # 256-bit AES key
        iv = os.urandom(12)  # 96-bit IV for GCM

        # Encrypt the file data with AES-GCM
        logger.info("Encrypting file data with AES-256-GCM...")
        print("Encrypting file data...")
        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        auth_tag = encryptor.tag

        logger.info(f"File encrypted: {len(ciphertext)} bytes ciphertext")

        # Encrypt the AES key with RSA using PKCS#1 v1.5 padding
        # (AEPGP cards use PKCS#1 v1.5 for PSO:DECIPHER, not OAEP)
        logger.info("Encrypting AES key with RSA-PKCS1v15...")
        print("Encrypting AES key with card's public key...")
        encrypted_aes_key = rsa_public_key.encrypt(
            aes_key,
            padding.PKCS1v15()
        )

        logger.info(f"AES key encrypted: {len(encrypted_aes_key)} bytes")

        # Write encrypted file with format:
        # [4 bytes: encrypted AES key length]
        # [encrypted AES key]
        # [12 bytes: IV]
        # [16 bytes: GCM auth tag]
        # [ciphertext]

        logger.debug(f"Writing encrypted data to: {output_file}")
        with open(output_file, 'wb') as f:
            # Write encrypted AES key length
            f.write(struct.pack('>I', len(encrypted_aes_key)))
            # Write encrypted AES key
            f.write(encrypted_aes_key)
            # Write IV
            f.write(iv)
            # Write GCM auth tag
            f.write(auth_tag)
            # Write ciphertext
            f.write(ciphertext)

        logger.info(f"Encrypted file written successfully: {output_file}")
        print(f"Encryption successful!")
        print(f"Encrypted file: {output_file}")

        return True, None

    except Exception as e:
        logger.error(f"Encryption failed with exception: {e}", e)
        import traceback
        logger.error(traceback.format_exc())
        return False, f"Encryption failed: {str(e)}"
