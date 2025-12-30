"""
AEPGP Card ATR Diagnostic Tool

This script detects your card and shows its ATR (Answer To Reset)
to help diagnose card detection issues.
"""

import sys
import io

# Force UTF-8 encoding for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

try:
    from smartcard.System import readers
    from smartcard.util import toHexString
except ImportError:
    print("ERROR: pyscard library not found.")
    print("Install it with: pip install pyscard")
    input("\nPress Enter to exit...")
    sys.exit(1)

print("=" * 60)
print("AEPGP Card ATR Diagnostic Tool")
print("=" * 60)
print()

# Get all readers
try:
    reader_list = readers()

    if not reader_list:
        print("ERROR: No smart card readers found!")
        print("Please connect your Gemalto card reader.")
        input("\nPress Enter to exit...")
        sys.exit(1)

    print(f"Found {len(reader_list)} reader(s):")
    for i, reader in enumerate(reader_list):
        print(f"  {i+1}. {reader}")
    print()

    # Try to connect to each reader
    for i, reader in enumerate(reader_list):
        print(f"Checking reader {i+1}: {reader}")
        print("-" * 60)

        try:
            connection = reader.createConnection()
            connection.connect()

            # Get ATR
            atr = connection.getATR()
            atr_hex = toHexString(atr)
            atr_list = list(atr)

            print(f"[OK] Card detected!")
            print(f"\nATR (hex):  {atr_hex}")
            print(f"ATR (list): {atr_list}")
            print(f"ATR length: {len(atr)} bytes")

            # Try to select OpenPGP applet
            print("\nTrying to select OpenPGP applet...")
            OPENPGP_AID = [0xD2, 0x76, 0x00, 0x01, 0x24, 0x01]
            SELECT_APDU = [0x00, 0xA4, 0x04, 0x00, len(OPENPGP_AID)] + OPENPGP_AID + [0x00]

            try:
                response, sw1, sw2 = connection.transmit(SELECT_APDU)
                status = f"{sw1:02X}{sw2:02X}"

                if sw1 == 0x90 and sw2 == 0x00:
                    print(f"[OK] OpenPGP applet selected successfully! (SW={status})")
                    print(f"Response: {toHexString(response)}")
                else:
                    print(f"[FAIL] Failed to select OpenPGP applet (SW={status})")

            except Exception as e:
                print(f"[FAIL] Error selecting applet: {e}")

            # Try GET VERSION command if available
            print("\nTrying GET VERSION command (0xF1)...")
            GET_VERSION = [0x00, 0xF1, 0x00, 0x00, 0x03]
            try:
                response, sw1, sw2 = connection.transmit(GET_VERSION)
                status = f"{sw1:02X}{sw2:02X}"
                if sw1 == 0x90 and sw2 == 0x00:
                    print(f"[OK] Version: {toHexString(response)} (SW={status})")
                else:
                    print(f"Version command returned: SW={status}")
            except Exception as e:
                print(f"Version command error: {e}")

            connection.disconnect()
            print()

        except Exception as e:
            print(f"[FAIL] No card in this reader or error: {e}")
            print()

    print("=" * 60)
    print("Diagnosis complete!")
    print()
    print("NEXT STEPS:")
    print("1. Copy the ATR (list) shown above")
    print("2. Share it to update the card detection code")
    print("=" * 60)

except Exception as e:
    print(f"ERROR: {e}")

input("\nPress Enter to exit...")
