# Bug Fix: Key Generation and Encryption Issue (v1.3.1)

## Problem Summary

After disabling PFX import feature in v1.3.0, encryption functionality stopped working with error:
```
couldn't read public key from the card
```

## Root Cause Analysis

The issue was in the key generation handler (`generate_keys_handler.py`):

1. **Old Implementation (Broken):**
   - Used subprocess to call `python -m smartpgp.highlevel generate-key dec`
   - The smartpgp.highlevel command-line interface had no actual CLI implementation
   - Commands ran without error but didn't actually generate keys on the card
   - Card key slots remained empty (Key Info showed `DE 06 01 00 02 00 03 00` - all zeros)

2. **Detection:**
   - APDU command `GET PUBLIC KEY` returned `SW=6A88` (referenced data not found)
   - Key Information data object showed all key slots as "not generated" (value 00)
   - Direct APDU testing confirmed no keys existed on card

## Solution

Rewrote `generate_keys_handler.py` to use **direct APDU commands** instead of subprocess:

### Key Changes:

1. **Direct Card Communication:**
   ```python
   # Connect to card using AEPGPCard class
   card = AEPGPCard()
   card.connect()
   ```

2. **Admin PIN Verification:**
   ```python
   # APDU: 00 20 00 83 Lc [PIN bytes]
   verify_apdu = [0x00, 0x20, 0x00, 0x83, len(pin_bytes)] + pin_bytes
   response, sw1, sw2 = card.connection.transmit(verify_apdu)
   ```

3. **Key Generation (APDU Command):**
   ```python
   # APDU: 00 47 80 00 02 B8 00 00
   # CLA=00, INS=47, P1=80 (generate), P2=00
   # Data: B8 00 (decryption slot + empty template)
   gen_apdu = [0x00, 0x47, 0x80, 0x00, 0x02, 0xB8, 0x00, 0x00]
   response, sw1, sw2 = card.connection.transmit(gen_apdu)
   ```

4. **Handle GET RESPONSE:**
   ```python
   # If SW=61XX, more data is available
   if sw1 == 0x61:
       get_response = [0x00, 0xC0, 0x00, 0x00, sw2]
       response2, sw1, sw2 = card.connection.transmit(get_response)
   ```

5. **Verification:**
   - After generation, verify key can be read with GET PUBLIC KEY command
   - Check status is SW=9000 or SW=61XX (success with more data)

### Additional Cleanup:

1. **Removed Unused Fallback Code:**
   - Deleted `read_public_key_using_smartpgp_module()` from card_key_reader.py
   - This function was attempting to use subprocess to call smartpgp module
   - Not needed since proper APDU commands work correctly

2. **Improved Error Messages:**
   - Changed SW=6A88 error from "trying fallback" to clear message:
     ```
     No key found in slot (SW=6A88)
     Please generate keys first using 'Generate Keys in Card' option
     ```

## Testing Results

### Before Fix:
```
Key Information: DE 06 01 00 02 00 03 00
                              ^^ DEC key = 00 (not generated)
Get Public Key: SW=6A88 (not found)
Encryption: FAILED
```

### After Fix:
```
Key Information: DE 06 01 00 02 01 03 00
                              ^^ DEC key = 01 (generated!)
Get Public Key: SW=610E (success, 270 bytes returned)
Encryption: SUCCESS - created .enc file
```

## Files Modified

1. **handlers/generate_keys_handler.py**
   - Complete rewrite to use direct APDU commands
   - Removed subprocess/smartpgp.highlevel approach
   - Added proper admin PIN verification
   - Added GET RESPONSE handling for large responses

2. **handlers/card_key_reader.py**
   - Removed `read_public_key_using_smartpgp_module()` function
   - Simplified error handling for SW=6A88

3. **VERSION**
   - Updated from 1.3.0 to 1.3.1

## Technical Details

### SmartPGP GENERATE KEY Command

**APDU Structure:**
- CLA: 00 (standard)
- INS: 47 (GENERATE ASYMMETRIC KEY PAIR)
- P1: 80 (generate both private and public key)
- P2: 00
- Lc: 02 (data length)
- Data: B8 00
  - B8 = Decryption/Encryption key slot
  - 00 = Empty template (use card defaults)
- Le: 00 (expect response)

**Response:**
- Public key data in TLV format (7F 49 ...)
- Length: 270 bytes for RSA-2048
- SW=61XX if more data available (need GET RESPONSE)
- SW=9000 on complete success

### Why Subprocess Approach Failed

The `smartpgp.highlevel` module is a Python library, not a CLI tool:
- Has no `__main__.py` entry point
- Running `python -m smartpgp.highlevel` does nothing
- No output to stdout/stderr
- Commands appear to succeed but don't execute

### Proper Implementation Pattern

For SmartPGP card operations:
1. ✓ Use smartcard library directly
2. ✓ Send APDU commands via connection.transmit()
3. ✓ Handle status words (SW1, SW2)
4. ✓ Use GET RESPONSE for large data (SW=61XX)
5. ✗ Don't use subprocess to call smartpgp module
6. ✗ Don't assume command-line interface exists

## Version History

- **v1.3.0** - Disabled PFX import, cleaned up test files
- **v1.3.1** - Fixed key generation using direct APDU commands

## Conclusion

The encryption feature now works correctly because keys are actually being generated on the card. The fix improves reliability by using direct card communication instead of subprocess calls, and provides better error messages when keys are missing.
