"""
AEPGP Card Detection and Management Utilities

This module provides utilities for detecting and communicating with AEPGP cards
on Windows systems.
"""

import sys
import os

try:
    from smartcard.System import readers
    from smartcard.Exceptions import NoCardException, CardConnectionException
    from smartcard.util import toHexString, toBytes
except ImportError:
    print("ERROR: pyscard library not found. Install it with: pip install pyscard")
    sys.exit(1)

# OpenPGP AID (Application Identifier)
OPENPGP_AID = [0xD2, 0x76, 0x00, 0x01, 0x24, 0x01]

# AmbiSecure Token ATR (Answer To Reset)
# Expected ATR: 3B D5 18 FF 81 B1 FE 45 1F C3 80 73 C8 21 10 6F
AMBISECURE_ATR = [0x3B, 0xD5, 0x18, 0xFF, 0x81, 0xB1, 0xFE, 0x45,
                  0x1F, 0xC3, 0x80, 0x73, 0xC8, 0x21, 0x10, 0x6F]


class AEPGPCard:
    """Represents a connection to an AEPGP card"""

    def __init__(self, connection):
        self.connection = connection
        self.reader = connection.getReader()

    def select_applet(self):
        """Select the OpenPGP applet on the card"""
        SELECT_APDU = [0x00, 0xA4, 0x04, 0x00, len(OPENPGP_AID)] + OPENPGP_AID + [0x00]
        response, sw1, sw2 = self.connection.transmit(SELECT_APDU)

        if sw1 != 0x90 or sw2 != 0x00:
            raise Exception(f"Failed to select OpenPGP applet: SW={sw1:02X}{sw2:02X}")

        return response

    def disconnect(self):
        """Close the connection to the card"""
        try:
            self.connection.disconnect()
        except:
            pass


def verify_ambisecure_atr(atr):
    """
    Verify if the ATR matches the AmbiSecure token.

    Args:
        atr: ATR bytes from the card

    Returns:
        bool: True if ATR matches AmbiSecure token, False otherwise
    """
    return list(atr) == AMBISECURE_ATR


def find_aepgp_card():
    """
    Search for an AmbiSecure AEPGP card in all available readers.
    Only accepts cards with the specific AmbiSecure ATR.

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

                # Get ATR and verify it's an AmbiSecure token
                atr = connection.getATR()
                if not verify_ambisecure_atr(atr):
                    # Not an AmbiSecure token, skip this card
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
