# SmartPGP APDU Buffer Limitation Issue

## Problem Summary

PFX import functionality fails with error code **6581** (`SW_MEMORY_FAILURE`) when attempting to import RSA-2048 private keys to the SmartPGP card.

## Root Cause

The error is **NOT a security timeout** but a **buffer overflow** in the SmartPGP JavaCard applet.

### Technical Details

**Buffer Limit:**
- SmartPGP's `INTERNAL_BUFFER_MAX_LENGTH` is hardcoded to **1280 bytes** (0x500)
- Location: `SmartPGP/src/fr/anssi/smartpgp/Constants.java:29`
```java
protected static final short INTERNAL_BUFFER_MAX_LENGTH = (short)0x500;
```

**Data Size Requirements:**
- RSA-2048 private key import requires **~1843 bytes** of data:
  - 7F48 template (key component metadata): ~800 bytes
  - 5F48 concatenated data (actual key material): ~900 bytes
  - 4D wrapper and TLV overhead: ~143 bytes

**Buffer Check Logic:**
- Location: `SmartPGP/src/fr/anssi/smartpgp/SmartPGPApplet.java:571-577`
```java
if((short)(off + lc) > Constants.INTERNAL_BUFFER_MAX_LENGTH) {
    transients.setChainingInput(false);
    transients.setChainingInputLength((short)0);
    ISOException.throwIt(Constants.SW_MEMORY_FAILURE);
    return;
}
```

**Error Code Definition:**
- Location: `SmartPGP/src/fr/anssi/smartpgp/Constants.java:52`
```java
protected static final short SW_MEMORY_FAILURE = (short)0x6581;
```

### Command Chaining Behavior

When using command chaining (CLA byte = 0x10) with 512-byte chunks:
1. **Chunk 1**: 512 bytes accumulated ✓
2. **Chunk 2**: 1024 bytes total accumulated ✓
3. **Chunk 3**: 1536 bytes total ❌ **EXCEEDS 1280-byte limit → Error 6581**

The SmartPGP applet accumulates all chained APDU data in the internal buffer before processing. When chunk 3 would push the total over 1280 bytes, it throws `SW_MEMORY_FAILURE`.

## Key Import Data Structure

The SmartPGP card requires both structures for RSA key import:

**7F48 - Private Key Template:**
- Tag 91: Public exponent (4 bytes)
- Tag 92: Prime p (128 bytes)
- Tag 93: Prime q (128 bytes)
- Tag 94: PQ (qinv) (128 bytes)
- Tag 95: DP1 (dp) (128 bytes)
- Tag 96: DQ1 (dq) (128 bytes)
- Tag 97: Modulus n (256 bytes)

**5F48 - Concatenated Data:**
- Raw concatenation of: e + p + q + qinv + dp + dq + n (~900 bytes)

**4D - Extended Header:**
- Wraps both 7F48 and 5F48 with key type indicator (B8 for decryption key)

**Source:** `SmartPGP/src/fr/anssi/smartpgp/PGPKey.java:importKey()` method requires both structures.

## Solution: Rebuild SmartPGP Applet

To fix this issue, the SmartPGP applet must be rebuilt with a larger buffer size.

### Required Changes

**File:** `SmartPGP/src/fr/anssi/smartpgp/Constants.java` (Line 29)

**Change:**
```java
// OLD (1280 bytes - insufficient for RSA-2048 import)
protected static final short INTERNAL_BUFFER_MAX_LENGTH = (short)0x500;

// NEW (2048 bytes - sufficient for RSA-2048 import)
protected static final short INTERNAL_BUFFER_MAX_LENGTH = (short)0x800;
```

### Rebuild Instructions

1. **Prerequisites:**
   - JavaCard Development Kit 3.0.4 or higher
   - Ant build tool
   - Java JDK 8 or higher

2. **Clone and Modify:**
   ```bash
   git clone https://github.com/github-af/SmartPGP.git
   cd SmartPGP
   # Edit src/fr/anssi/smartpgp/Constants.java (line 29)
   # Change 0x500 to 0x800
   ```

3. **Build:**
   ```bash
   ant
   ```
   Output: `SmartPGPApplet.cap` file

4. **Install to Card:**
   ```bash
   # Delete old applet
   gp --delete D276000124010304AEPGPV1.0

   # Install new applet
   gp --install SmartPGPApplet.cap
   ```

## Alternative Solutions (Not Recommended)

### Option 1: Use Smaller Key Size
- Import RSA-1024 instead of RSA-2048
- **Security Risk:** RSA-1024 is deprecated and considered weak

### Option 2: Generate Keys On-Card
- Use GENERATE ASYMMETRIC KEY PAIR command instead of importing
- **Limitation:** Cannot import existing keys from PFX files

## Implementation Status

**Current Version:** 1.2.12

**Status:** Awaiting SmartPGP applet rebuild with larger buffer

**Workaround:** None available without applet modification

## References

### SmartPGP Source Files
- [Constants.java](https://github.com/github-af/SmartPGP/blob/master/src/fr/anssi/smartpgp/Constants.java) - Buffer size constants
- [SmartPGPApplet.java](https://github.com/github-af/SmartPGP/blob/master/src/fr/anssi/smartpgp/SmartPGPApplet.java) - Command chaining and buffer validation
- [PGPKey.java](https://github.com/github-af/SmartPGP/blob/master/src/fr/anssi/smartpgp/PGPKey.java) - Key import format requirements

### Related Documentation
- [OpenPGP Card Specification 3.4](https://www.gnupg.org/ftp/specs/OpenPGP-smart-card-application-3.4.pdf)
- [JavaCard OwnerPIN API](https://docs.oracle.com/javacard/3.0.5/api/javacard/framework/OwnerPIN.html)

## Version History

- **1.2.4**: Initial PFX import implementation with command chaining (255-byte chunks)
- **1.2.5**: Bug fix for wrong length error (6700)
- **1.2.6**: Attempted security timeout fix (moved PIN verification)
- **1.2.7**: Attempted extended APDU approach
- **1.2.8**: Re-verify PIN before every chunk
- **1.2.9**: Re-verify PIN every 4 chunks to avoid anti-brute-force
- **1.2.10**: Reactive PIN re-verification only on 6581 error
- **1.2.11**: Extended APDU with 3-byte Lc encoding
- **1.2.12**: Increased chunk size to 512 bytes (still fails at chunk 3)

## Error Code Reference

- **6700**: Wrong length - APDU command too large
- **6581**: Memory failure - Internal buffer capacity exceeded
- **6883**: Authentication method blocked - Too many PIN verification attempts
- **6982**: Security status not satisfied - PIN not verified
- **6A80**: Incorrect parameters in command data field
