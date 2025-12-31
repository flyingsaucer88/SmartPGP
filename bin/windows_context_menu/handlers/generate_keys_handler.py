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

    Uses the smartpgp.highlevel module to generate keys.
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

        # Import smartpgp highlevel module
        try:
            import subprocess

            # Add bin directory to Python path for smartpgp module
            bin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            smartpgp_dir = os.path.join(bin_dir, 'smartpgp')

            # Use smartpgp.highlevel to generate keys
            # First, switch to RSA-2048 for decryption key
            logger.info("Switching decryption key slot to RSA-2048...")
            env = os.environ.copy()
            env['PYTHONPATH'] = bin_dir + os.pathsep + env.get('PYTHONPATH', '')

            result = subprocess.run(
                [sys.executable, "-m", "smartpgp.highlevel", "--reader", "0", "switch-key", "dec", "rsa2048"],
                capture_output=True,
                text=True,
                timeout=30,
                env=env
            )

            if result.returncode != 0:
                error_msg = f"Failed to switch key slot: {result.stderr}"
                logger.error(error_msg)
                card_utils.show_error_dialog(
                    f"Failed to switch key slot:\n\n{result.stderr}",
                    "Key Generation Error"
                )
                logger.log_operation_end("Generate Keys", False, error_msg)
                return

            logger.info("Key slot switched to RSA-2048")

            # Generate the key
            logger.info("Generating RSA-2048 key pair on card...")
            card_utils.show_info_dialog(
                "Generating RSA-2048 key pair...\n\n"
                "This may take 30-60 seconds.\n"
                "Please wait...",
                "Generating Keys"
            )

            result = subprocess.run(
                [sys.executable, "-m", "smartpgp.highlevel", "--reader", "0", "generate-key", "dec"],
                capture_output=True,
                text=True,
                timeout=120,
                env=env
            )

            if result.returncode != 0:
                error_msg = f"Key generation failed: {result.stderr}"
                logger.error(error_msg)
                card_utils.show_error_dialog(
                    f"Key generation failed:\n\n{result.stderr}",
                    "Key Generation Error"
                )
                logger.log_operation_end("Generate Keys", False, error_msg)
                return

            logger.info("Key generation successful!")
            logger.info(f"Output: {result.stdout}")

            # Success!
            card_utils.show_info_dialog(
                "RSA-2048 key pair generated successfully!\n\n"
                "Slot: Decryption/Encryption\n"
                "Algorithm: RSA-2048\n\n"
                "The key pair is now stored securely on your AEPGP card.\n"
                "The private key will never leave the card.",
                "Key Generation Successful"
            )
            logger.log_operation_end("Generate Keys", True)

        except subprocess.TimeoutExpired:
            error_msg = "Key generation timed out (exceeded 2 minutes)"
            logger.error(error_msg)
            card_utils.show_error_dialog(
                "Key generation timed out.\n\n"
                "Please try again. If the problem persists,\n"
                "try resetting the card.",
                "Key Generation Timeout"
            )
            logger.log_operation_end("Generate Keys", False, error_msg)

        except ImportError:
            error_msg = "smartpgp module not found"
            logger.error(error_msg)
            card_utils.show_error_dialog(
                "The smartpgp module is not installed.\n\n"
                "Please install it with:\n"
                "pip install smartpgp",
                "Module Not Found"
            )
            logger.log_operation_end("Generate Keys", False, error_msg)

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
