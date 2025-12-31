"""
AEPGP Card Detection and Management Utilities

This module provides utilities for detecting and communicating with AEPGP cards
on Windows systems.
"""

import sys
import os

# Import debug logger
try:
    from debug_logger import get_logger
    logger = get_logger()
except ImportError:
    # Fallback if logger not available
    class DummyLogger:
        def info(self, msg): pass
        def error(self, msg, e=None): pass
        def debug(self, msg): pass
    logger = DummyLogger()

try:
    from smartcard.System import readers
    from smartcard.Exceptions import NoCardException, CardConnectionException
    from smartcard.util import toHexString, toBytes
except ImportError:
    print("ERROR: pyscard library not found. Install it with: pip install pyscard")
    sys.exit(1)

# OpenPGP AID (Application Identifier)
OPENPGP_AID = [0xD2, 0x76, 0x00, 0x01, 0x24, 0x01]

# Supported ATRs (Answer To Reset) for AEPGP/SmartPGP cards
# Multiple ATRs are supported to work with different card manufacturers
SUPPORTED_ATRS = [
    # Original AmbiSecure Token ATR
    [0x3B, 0xD5, 0x18, 0xFF, 0x81, 0xB1, 0xFE, 0x45, 0x1F, 0xC3, 0x80, 0x73, 0xC8, 0x21, 0x10, 0x6F],
    # SmartPGP on Gemalto/NXP JCOP cards: 3B D5 18 FF 81 91 FE 1F C3 80 73 C8 21 10 0A
    [0x3B, 0xD5, 0x18, 0xFF, 0x81, 0x91, 0xFE, 0x1F, 0xC3, 0x80, 0x73, 0xC8, 0x21, 0x10, 0x0A],
]


class AEPGPCard:
    """Represents a connection to an AEPGP card"""

    def __init__(self, connection):
        self.connection = connection
        self.reader = connection.getReader()

    def _log_apdu(self, command, response, sw1, sw2):
        """Log APDU command and response"""
        cmd_hex = toHexString(command)
        resp_hex = toHexString(response) if response else ""
        logger.debug(f"APDU CMD: {cmd_hex}")
        logger.debug(f"APDU RSP: {resp_hex} SW={sw1:02X}{sw2:02X}")

    def select_applet(self):
        """Select the OpenPGP applet on the card"""
        SELECT_APDU = [0x00, 0xA4, 0x04, 0x00, len(OPENPGP_AID)] + OPENPGP_AID + [0x00]
        logger.info("Selecting OpenPGP applet...")
        response, sw1, sw2 = self.connection.transmit(SELECT_APDU)
        self._log_apdu(SELECT_APDU, response, sw1, sw2)

        if sw1 != 0x90 or sw2 != 0x00:
            error_msg = f"Failed to select OpenPGP applet: SW={sw1:02X}{sw2:02X}"
            logger.error(error_msg)
            raise Exception(error_msg)

        logger.info("OpenPGP applet selected successfully")
        return response

    def disconnect(self):
        """Close the connection to the card"""
        try:
            self.connection.disconnect()
        except:
            pass


def verify_supported_atr(atr):
    """
    Verify if the ATR matches any supported AEPGP/SmartPGP card.

    Args:
        atr: ATR bytes from the card

    Returns:
        bool: True if ATR matches a supported card, False otherwise
    """
    atr_list = list(atr)
    return any(atr_list == supported_atr for supported_atr in SUPPORTED_ATRS)


def find_aepgp_card():
    """
    Search for an AEPGP/SmartPGP card in all available readers.
    Supports multiple card types with different ATRs.

    Returns:
        tuple: (AEPGPCard object, None) on success
               (None, error_message) on failure
    """
    try:
        reader_list = readers()

        if not reader_list:
            return None, "No smart card readers found.\n\nPlease connect a USB smart card reader to your computer."

        # Try each reader
        for reader in reader_list:
            try:
                connection = reader.createConnection()
                connection.connect()

                # Get ATR and verify it's a supported card
                atr = connection.getATR()
                if not verify_supported_atr(atr):
                    # Not a supported card, skip this card
                    try:
                        connection.disconnect()
                    except:
                        pass
                    continue

                # Try to select OpenPGP applet
                card = AEPGPCard(connection)
                card.select_applet()

                # Success!
                return card, None

            except NoCardException:
                # No card in this reader, try next one
                continue
            except CardConnectionException:
                # Connection failed, try next reader
                continue
            except Exception as e:
                # Card present but wrong applet or wrong card, try next reader
                try:
                    connection.disconnect()
                except:
                    pass
                continue

        # No AEPGP card found in any reader
        return None, "AEPGP card not found.\n\nPlease insert your AEPGP card into the reader."

    except Exception as e:
        return None, f"Error accessing smart card:\n\n{str(e)}"


def get_card_info(card):
    """
    Get basic information about the AEPGP card.

    Args:
        card: AEPGPCard object

    Returns:
        dict: Card information
    """
    try:
        # GET DATA command for application related data (0x00 0x6E)
        GET_DATA = [0x00, 0xCA, 0x00, 0x6E, 0x00]
        response, sw1, sw2 = card.connection.transmit(GET_DATA)

        info = {
            'reader': card.reader,
            'connected': True,
            'response_status': f"{sw1:02X}{sw2:02X}"
        }

        return info
    except Exception as e:
        return {
            'reader': card.reader,
            'connected': True,
            'error': str(e)
        }


def show_error_dialog(message, title="AEPGP"):
    """
    Show an error message dialog on Windows.

    Args:
        message: Error message to display
        title: Dialog title
    """
    try:
        import ctypes
        MessageBox = ctypes.windll.user32.MessageBoxW
        # MB_ICONERROR | MB_OK = 0x10 | 0x00
        MessageBox(None, message, title, 0x10)
    except Exception as e:
        print(f"ERROR: {message}")


def show_info_dialog(message, title="AEPGP"):
    """
    Show an information message dialog on Windows.

    Args:
        message: Information message to display
        title: Dialog title
    """
    try:
        import ctypes
        MessageBox = ctypes.windll.user32.MessageBoxW
        # MB_ICONINFORMATION | MB_OK = 0x40 | 0x00
        MessageBox(None, message, title, 0x40)
    except Exception as e:
        print(f"INFO: {message}")


def show_question_dialog(message, title="AEPGP"):
    """
    Show a yes/no question dialog on Windows.

    Args:
        message: Question to ask
        title: Dialog title

    Returns:
        bool: True if user clicked Yes, False otherwise
    """
    try:
        import ctypes
        MessageBox = ctypes.windll.user32.MessageBoxW
        # MB_ICONQUESTION | MB_YESNO = 0x20 | 0x04
        # Returns IDYES (6) or IDNO (7)
        result = MessageBox(None, message, title, 0x24)
        return result == 6  # IDYES
    except Exception as e:
        print(f"QUESTION: {message}")
        return False


if __name__ == "__main__":
    # Test the card detection
    print("Searching for AEPGP card...")
    card, error = find_aepgp_card()

    if error:
        print(f"Error: {error}")
        sys.exit(1)

    print(f"AEPGP card found in reader: {card.reader}")

    # Print ATR
    atr = card.connection.getATR()
    print(f"ATR: {toHexString(atr)}")

    info = get_card_info(card)
    print(f"Card info: {info}")

    card.disconnect()
    print("Disconnected successfully")
