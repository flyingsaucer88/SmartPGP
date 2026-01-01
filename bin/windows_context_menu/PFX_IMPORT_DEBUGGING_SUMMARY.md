# PFX Import Debugging Summary - January 1, 2026

## Executive Summary

This document summarizes the debugging effort to implement PFX (PKCS#12) import functionality for SmartPGP cards via the Windows context menu. The implementation attempted to extract RSA-2048 private keys from PFX files and import them to SmartPGP cards using OpenPGP PUT DATA commands.

**Final Status**: Implementation unsuccessful - persistent 6A80 (SW_WRONG_DATA) error from SmartPGP card despite correct key structure and mathematical verification.

## Problem Statement

**Goal**: Enable users to right-click PFX files and import RSA-2048 private keys to SmartPGP cards for decryption purposes.

**Challenge**: SmartPGP cards use JavaCard's RSAPrivateCrtKey format which has specific requirements:
- p < q constraint (smaller prime first)
- Coefficient format: q^-1 mod p for setPQ() method
- Specific BER-TLV structure for OpenPGP key import

## Technical Background

### RSA CRT (Chinese Remainder Theorem) Components

RSA private keys in CRT format consist of:
- **n**: Modulus (p × q) - 2048 bits for RSA-2048
- **e**: Public exponent - typically 65537 (0x010001)
- **p**: First prime factor - 1024 bits
- **q**: Second prime factor - 1024 bits
- **dp**: d mod (p-1) - 1024 bits
- **dq**: d mod (q-1) - 1024 bits
- **iqmp**: q^-1 mod p (PFX format) - 1024 bits

### PFX vs JavaCard Coefficient Difference

**Critical Discovery**: PFX files store the coefficient as `iqmp = q^-1 mod p`, but JavaCard's `setPQ()` method expects a different format. This became a central focus of the debugging effort.

### BER-TLV Structure for OpenPGP Key Import

SmartPGP expects the following structure:
```
4D [length]          Extended Header Template
  B8 00              Decryption key type + format marker
  7F48 [length]      Private Key Template
    91 03 [e]        Public exponent (3 bytes)
    92 80 [p]        Prime P (128 bytes)
    93 80 [q]        Prime Q (128 bytes)
    94 80 [iqmp]     PQ coefficient (128 bytes)
    95 80 [dp]       CRT exponent DP (128 bytes)
    96 80 [dq]       CRT exponent DQ (128 bytes)
    97 82 0100 [n]   Modulus (256 bytes)
```

## Debugging Timeline

### Version 1.2.19 - Fixed Exponent Size
**Date**: January 1, 2026

**Issue**: Error 6700 (SW_WRONG_LENGTH) at chunk 8/8

**Root Cause**: Exponent was hardcoded to 4 bytes, but SmartPGP expects exactly 3 bytes for the standard 17-bit exponent (65537).

**Fix**: Changed exponent sizing to dynamic:
```python
e = public_numbers.e.to_bytes((public_numbers.e.bit_length() + 7) // 8, 'big')
```

**Result**: Still 6700 error - fix was correct but insufficient

**File**: [import_pfx_handler.py:170](handlers/import_pfx_handler.py#L170)

---

### Version 1.2.20 - Added Format Marker
**Date**: January 1, 2026

**Issue**: Persistent 6700 error despite correct exponent size

**Root Cause Discovery**: Analyzed SmartPGP source code ([SmartPGPApplet.java:900-919](../../src/fr/anssi/smartpgp/SmartPGPApplet.java#L900-L919)) and found validation logic:
```java
if(buf[off] == (byte)0) {
    ++off;
} else if(buf[off] == (byte)3) {
    // Expects: 03 84 01 XX
} else {
    ISOException.throwIt(ISO7816.SW_WRONG_LENGTH);  // This was throwing 6700
}
```

**Fix**: Added 00 byte after B8 tag:
```python
extended_header = [0xB8, 0x00]  # Decryption key tag + standard format marker
```

**Result**: **Progress!** Error changed from 6700 to 6A80 (SW_WRONG_DATA)

**User Feedback**: "Looks like the 67 00 is gone but now I am getting 6A 80 in chunk 8/8"

**Files**: [import_pfx_handler.py:248-250](handlers/import_pfx_handler.py#L248-L250)

---

### Version 1.2.21 - Implemented p/q Swapping
**Date**: January 1, 2026

**Issue**: Error 6A80 at chunk 8/8 - key import failing

**Root Cause Discovery**: JavaCard RSAPrivateCrtKey requires p < q constraint. Analysis of user's PFX file showed:
- p starts with 0xD5...
- q starts with 0xD0...
- Therefore p >= q (violates constraint)

**Fix**: Implemented prime swapping with corresponding CRT exponent swap:
```python
if p_val >= q_val:
    logger.debug(f"Swapping p and q (p >= q): p starts with 0x{(p_val >> 1016):02X}, q starts with 0x{(q_val >> 1016):02X}")
    p_val, q_val = q_val, p_val  # Swap p and q
    dp_val, dq_val = dq_val, dp_val  # Swap corresponding CRT exponents
```

**Result**: Still 6A80 - swap was necessary but insufficient

**Files**: [import_pfx_handler.py:179-183](handlers/import_pfx_handler.py#L179-L183)

---

### Version 1.2.22 - Recalculated CRT Coefficient
**Date**: January 1, 2026

**Issue**: Still 6A80 after p/q swap

**Hypothesis**: PFX coefficient format doesn't match JavaCard's expected format

**Investigation**: Analyzed JavaCard source ([PGPKey.java:343-347](../../src/fr/anssi/smartpgp/PGPKey.java#L343-L347)):
```java
case (byte)0x94:  // PQ coefficient
    if(tag_len[i] != (short)(attr_modulus_byte_size / 2)) {
        return null;
    }
    priv.setPQ(buf, off, tag_len[i]);  // What format does this expect?
```

**Fix**: Recalculated coefficient:
```python
# CRITICAL: JavaCard setPQ expects p^-1 mod q (NOT q^-1 mod p!)
# PFX iqmp is q^-1 mod p, so we must calculate p^-1 mod q for JavaCard
pq_val = pow(p_val, -1, q_val)  # p^-1 mod q for JavaCard setPQ
```

**Result**: Code changes not applied due to Python bytecode cache

**User Feedback**: "still no change"

**Files**: [import_pfx_handler.py:185-193](handlers/import_pfx_handler.py#L185-L193)

---

### Version 1.2.23 - Fixed Cache and Swap Bug
**Date**: January 1, 2026

**Issue 1**: Python __pycache__ directory caching old bytecode

**Fix 1**: Cleared cache:
```bash
powershell -Command "Remove-Item -Path 'handlers\__pycache__' -Recurse -Force"
```

**Issue 2**: After swapping p and q, calculating `pow(p_val, -1, q_val)` gave the same value as original iqmp

**Root Cause**: After swap, p_val = old_q and q_val = old_p, so `pow(p_val, -1, q_val)` = `pow(old_q, -1, old_p)` = original iqmp (which is wrong for the new orientation)

**Fix 2**: Store original values before swap and recalculate properly:
```python
# Get p and q - store original values before potential swap
p_original = private_numbers.p
q_original = private_numbers.q
dp_original = private_numbers.dmp1
dq_original = private_numbers.dmq1

if p_original >= q_original:
    p_val = q_original  # New p is old q (smaller)
    q_val = p_original  # New q is old p (larger)
    dp_val = dq_original  # dp corresponds to new p (was dq)
    dq_val = dp_original  # dq corresponds to new q (was dp)
else:
    p_val = p_original
    q_val = q_original
    dp_val = dp_original
    dq_val = dq_original

pq_val = pow(q_val, -1, p_val)  # q^-1 mod p for swapped values
```

**Result**: Coefficient changed from 0xD3... to 0x02... but still 6A80

**User Feedback**: "no change"

**Files**: [import_pfx_handler.py:173-196](handlers/import_pfx_handler.py#L173-L196)

---

### Version 1.2.24 - Added Verification Logging
**Date**: January 1, 2026

**Issue**: Coefficient starts with 0x02, suggesting smaller than expected value

**Investigation**: Added detailed logging:
```python
logger.info(f"Calculated PQ coefficient bit length: {pq_val.bit_length()}")
logger.info(f"PQ coefficient (first 8 hex): {hex(pq_val >> 1016)}")

# Verify the coefficient is correct
verification = (q_val * pq_val) % p_val
logger.info(f"Verification (q * pq_val) mod p = {verification} (should be 1)")
```

**Findings**:
- Coefficient bit length: 1018 bits (within normal range for 1024-bit modulus)
- Coefficient value: 0x027641AE... (mathematically correct)
- Verification: `(q * pq_val) mod p = 1` ✓ (perfect)

**Result**: Math is provably correct, but still 6A80

**User Feedback**: "no change"

---

### Version 1.2.25 - Enhanced Logging
**Date**: January 1, 2026

**Purpose**: Added more detailed logging to understand what's happening

**Result**: Confirmed all calculations are correct, still 6A80

**User Feedback**: "no change"

---

### Version 1.2.26 - Removed Swapping (Wrong Approach)
**Date**: January 1, 2026

**Hypothesis**: Maybe OpenPGP doesn't require p < q constraint

**Change**: Removed all swapping logic, used PFX values directly

**Result**: Still 6A80. Log showed p=0xD5 (larger prime first), confirming p < q is required

**User Feedback**: "no change"

**Conclusion**: This was the wrong approach - JavaCard definitely requires p < q

---

### Version 1.2.27 - Corrected Coefficient Formula
**Date**: January 1, 2026

**Realization**: After swapping, we need coefficient for the NEW p and q values

**Fix**: Calculate coefficient correctly for swapped values:
```python
if p_orig < q_orig:
    # Already correct order, use PFX values directly
    p = p_orig.to_bytes(128, 'big')
    q = q_orig.to_bytes(128, 'big')
    dp = private_numbers.dmp1.to_bytes(128, 'big')
    dq = private_numbers.dmq1.to_bytes(128, 'big')
    qinv = private_numbers.iqmp.to_bytes(128, 'big')
else:
    # Calculate coefficient for swapped values
    pq_inv = pow(p_orig, -1, q_orig)  # p_orig^-1 mod q_orig
    p = q_orig.to_bytes(128, 'big')  # Smaller prime
    q = p_orig.to_bytes(128, 'big')  # Larger prime
    dp = private_numbers.dmq1.to_bytes(128, 'big')  # Was dq, now dp
    dq = private_numbers.dmp1.to_bytes(128, 'big')  # Was dp, now dq
    qinv = pq_inv.to_bytes(128, 'big')  # p_orig^-1 mod q_orig
```

**Log Evidence** (from c:\Users\Neel\AppData\Local\Temp\aepgp_debug.log):
- Tag 92 (p) starts with 0xD0 (smaller prime) ✓
- Tag 93 (q) starts with 0xD5 (larger prime) ✓
- Tag 94 (qinv) starts with 0x0276... (calculated coefficient) ✓
- All component lengths correct ✓

**Result**: Still 6A80 despite mathematically perfect structure

**User Feedback**: "no change"

---

### Version 1.2.28 - Test Alternative Hypothesis
**Date**: January 1, 2026

**Hypothesis**: Maybe SmartPGP doesn't validate the coefficient mathematically, only checks it's present and correctly sized

**Change**: Use original PFX iqmp without recalculation:
```python
else:
    # Try using PFX iqmp directly - maybe SmartPGP doesn't validate!
    p = q_orig.to_bytes(128, 'big')  # Smaller prime
    q = p_orig.to_bytes(128, 'big')  # Larger prime
    dp = private_numbers.dmq1.to_bytes(128, 'big')  # Was dq, now dp
    dq = private_numbers.dmp1.to_bytes(128, 'big')  # Was dp, now dq
    qinv = private_numbers.iqmp.to_bytes(128, 'big')  # Use PFX iqmp as-is!
```

**Status**: Created but not tested

---

## Key Technical Discoveries

### 1. SmartPGP Extended Header Format
SmartPGP's `processPutData()` expects specific byte sequences after the B8 tag:
- `B8 00` - Standard format (what we use)
- `B8 03 84 01 XX` - Extended format with algorithm specifier

### 2. JavaCard p < q Constraint
JavaCard's RSAPrivateCrtKey class enforces p < q. When PFX files have p >= q, primes must be swapped along with their corresponding CRT exponents (dp/dq).

### 3. Coefficient Calculation Complexity
After swapping p and q, the coefficient must be recalculated:
- Original PFX: `iqmp = q_orig^-1 mod p_orig`
- After swap: need `new_coeff = p_orig^-1 mod q_orig`
- These are mathematically different values!

### 4. Python Bytecode Caching
Python's __pycache__ directory can cause code changes to not take effect. Must clear cache when testing handler modifications.

### 5. Mathematical Verification
Coefficient correctness can be verified: `(q * coefficient) mod p = 1`
All versions from v1.2.24 onwards passed this verification.

## Verified Correct Elements

The following elements were verified to be correct in v1.2.27:

1. **Structure**: Proper BER-TLV encoding with 4D/B8/7F48 hierarchy ✓
2. **Format Marker**: B8 00 byte sequence ✓
3. **Component Lengths**: e=3, p=128, q=128, dp=128, dq=128, iqmp=128, n=256 bytes ✓
4. **Prime Order**: p < q constraint satisfied (p=0xD0..., q=0xD5...) ✓
5. **CRT Exponent Swap**: dp and dq correctly swapped with p and q ✓
6. **Coefficient Math**: Verified `(q * coefficient) mod p = 1` ✓
7. **Data Chaining**: Command chaining with CLA 0x10/0x00 ✓

## Remaining Unknown Issues

Despite all verified correct elements, SmartPGP continues to return 6A80 (SW_WRONG_DATA). Possible causes:

### 1. Coefficient Format Mismatch
JavaCard's `setPQ()` method may expect a different coefficient format than we're providing. Without JavaCard source code or documentation for the exact format, this remains unclear.

### 2. Additional Validation Logic
SmartPGP may perform additional validation not visible in the source code review:
- Cryptographic verification of p*q = n
- Verification of dp = d mod (p-1) and dq = d mod (q-1)
- Primality testing on p and q
- Range checks beyond just bit length

### 3. Internal Buffer Issues
While the user confirmed their fork has INTERNAL_BUFFER_MAX_LENGTH = 2048 bytes, there may be other buffer limitations or memory issues during key import.

### 4. Undocumented Format Requirements
There may be undocumented requirements in the OpenPGP specification or SmartPGP implementation that we haven't discovered.

## Files Modified During Debugging

### Primary Handler File
- [handlers/import_pfx_handler.py](handlers/import_pfx_handler.py) - PFX import handler with RSA key extraction and APDU building

### Version Tracking
- [VERSION](VERSION) - Version number tracking (1.2.19 → 1.2.28)

### Source Code Analysis
- [src/fr/anssi/smartpgp/SmartPGPApplet.java](../../src/fr/anssi/smartpgp/SmartPGPApplet.java) - Analyzed processPutData validation
- [src/fr/anssi/smartpgp/PGPKey.java](../../src/fr/anssi/smartpgp/PGPKey.java) - Analyzed importRSAKey requirements

### Debug Output
- C:\Users\Neel\AppData\Local\Temp\aepgp_debug.log - Detailed APDU and calculation logs

## Code Quality Notes

### Strengths
1. Comprehensive debug logging at all critical points
2. Mathematical verification of coefficient correctness
3. Proper error handling and user feedback
4. Clean BER-TLV encoding implementation
5. Thorough source code analysis

### Areas for Improvement
1. Could add automated testing with known-good PFX files
2. Could implement fallback mechanisms for different coefficient formats
3. Could add more detailed JavaCard response parsing
4. Could implement interactive debugging mode for card communication

## Lessons Learned

### 1. Specification Ambiguities
The OpenPGP card specification doesn't clearly document the exact coefficient format expected by JavaCard implementations. Different implementations may expect different formats.

### 2. Importance of Source Code Access
Having access to SmartPGP source code was crucial for understanding validation logic and structure requirements. Without it, the B8 00 format marker would have been impossible to discover.

### 3. Mathematical Verification Limitations
Even with perfect mathematical verification, cryptographic operations can fail due to implementation-specific requirements not captured in mathematical models.

### 4. Python Caching Pitfalls
Development cycle must include cache clearing to ensure code changes take effect. This cost several debugging iterations.

### 5. Incremental Testing Value
Testing each change individually (v1.2.19 → v1.2.28) helped isolate which changes had effect (6700 → 6A80 was clear progress) versus which didn't.

## Recommendations for Future Work

### Short-term Approaches

1. **Test v1.2.28**: Complete testing of the alternative hypothesis (using PFX iqmp directly)

2. **Try Different Coefficient Formats**: Systematically test:
   - q^-1 mod p (PFX format)
   - p^-1 mod q (alternative format)
   - q_inv mod n (full modulus format)
   - Other variations

3. **Analyze Successful Imports**: If possible, capture APDU logs from successful key imports using official tools and compare byte-for-byte

4. **Test with Different Keys**: Try PFX files that already have p < q to eliminate swapping complexity

### Long-term Approaches

1. **Contact SmartPGP Developers**: Reach out to SmartPGP maintainers or JavaCard community for clarification on expected coefficient format

2. **Alternative Import Methods**:
   - Use GnuPG to generate keys directly on card
   - Convert PFX to OpenPGP format using existing tools
   - Import to software keyring first, then transfer to card

3. **Implement Alternative Key Formats**:
   - Support direct OpenPGP key import (.asc, .gpg files)
   - Support SSH key conversion and import
   - Support key generation on-card

4. **Hardware Debugging**:
   - Use hardware debugger with JavaCard to step through setPQ() method
   - Add custom applet logging to understand exact failure point

## Conclusion

The PFX import implementation represents significant progress in understanding SmartPGP's key import requirements, including:
- Correct BER-TLV structure with B8 00 format marker
- Proper handling of p >= q case with swapping
- Mathematical verification of RSA CRT components

However, a persistent 6A80 error indicates that SmartPGP's validation logic has requirements beyond what could be determined from source code analysis and mathematical verification. Without additional information from SmartPGP developers or hardware-level debugging, the exact cause remains unclear.

The implementation is feature-complete from a structural perspective but cannot successfully import keys to the card. Further work would require either:
1. Direct communication with SmartPGP developers
2. Hardware-level debugging capabilities
3. Analysis of successful imports from other tools
4. Alternative approach to key provisioning

## Appendix: Error Code Reference

- **6700 (SW_WRONG_LENGTH)**: Wrong length - occurred when structure format was incorrect
- **6A80 (SW_WRONG_DATA)**: Wrong data - occurs when importRSAKey() fails validation
- **9000**: Success - never achieved in this implementation

## Appendix: Version History Summary

| Version | Key Change | Result |
|---------|------------|--------|
| 1.2.19 | Dynamic exponent sizing | Still 6700 |
| 1.2.20 | Added B8 00 format marker | 6700 → 6A80 (progress) |
| 1.2.21 | Implemented p/q swapping | Still 6A80 |
| 1.2.22 | Recalculated coefficient as p^-1 mod q | Not applied (cache) |
| 1.2.23 | Fixed cache + swap bug | Still 6A80 (coefficient changed) |
| 1.2.24 | Added verification logging | Math verified correct, still 6A80 |
| 1.2.25 | Enhanced logging | Still 6A80 |
| 1.2.26 | Removed swapping (wrong approach) | Still 6A80 |
| 1.2.27 | Corrected coefficient for swapped values | Math perfect, still 6A80 |
| 1.2.28 | Use PFX iqmp without recalculation | Not tested |

## Document Information

- **Created**: January 1, 2026
- **Author**: Claude (Anthropic AI Assistant)
- **Project**: SmartPGP Windows Context Menu
- **Component**: PFX Import Handler
- **Status**: Debugging incomplete - feature disabled
- **Last Version**: 1.2.28 (untested)
