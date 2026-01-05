# AEPGP Android NFC Implementation Guide

**Date**: 2026-01-05
**Branch**: Androidgpg
**Status**: 🚀 NFC-Based Implementation

---

## Overview

This document describes the NFC-based implementation of AEPGP Android Encryptor. **NFC is much more practical than USB OTG** because:

✅ **Most Android phones have NFC built-in** (no external hardware needed)
✅ **Simpler implementation** (Android NFC API is well-supported)
✅ **Better user experience** (just tap card to phone)
✅ **More portable** (no cables or adapters needed)
✅ **Lower power consumption**
✅ **Faster setup** (no USB permissions hassle)

---

## NFC vs USB OTG Comparison

| Aspect | NFC | USB OTG |
|--------|-----|---------|
| **Hardware Required** | None (built into phone) | External USB card reader + OTG adapter |
| **Device Compatibility** | Most Android phones (90%+) | Limited (requires USB Host support) |
| **User Experience** | Tap card to phone | Connect reader, insert card, manage cables |
| **Implementation** | Native Android NFC API | Complex CCID protocol implementation |
| **Power** | Low power (battery friendly) | Higher power (USB + reader) |
| **Cost** | $0 (already in phone) | $15-30 (reader + adapter) |
| **Portability** | Excellent (no accessories) | Poor (bulky setup) |
| **Setup Time** | Instant (tap) | 30-60 seconds (connect, wait) |

**Winner**: NFC is clearly superior for Android!

---

## How NFC Works with Smart Cards

### NFC Technology

**NFC (Near Field Communication)**:
- Short-range wireless technology (< 4cm)
- Based on ISO 14443 standard
- Operates at 13.56 MHz
- Supports ISO-DEP (ISO 14443-4) for smart cards

### Android NFC Support

**Android NFC API**:
- Available since Android 2.3 (API 9)
- Mature and well-documented
- Built-in support for ISO-DEP cards
- No external libraries needed!

**NFC Card Communication Flow**:
```
┌──────────────────┐
│  Android Device  │
│  (with NFC)      │
└────────┬─────────┘
         │ NFC Radio (13.56 MHz)
         │ < 4cm distance
         ▼
┌──────────────────┐
│  AEPGP Card      │
│  (ISO 14443-4)   │
└──────────────────┘
```

### APDU Communication via NFC

1. **User taps card to phone** - NFC discovers ISO-DEP card
2. **Android notifies app** - Intent with `IsoDep` tag
3. **App connects** - `IsoDep.connect()`
4. **App sends APDU** - `IsoDep.transceive(apdu)`
5. **Card responds** - Returns response data + status
6. **App processes** - Parse response, continue operations
7. **App disconnects** - `IsoDep.close()`

---

## Architecture for NFC Implementation

### Updated Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Android Application                     │
├─────────────────────────────────────────────────────────────┤
│  UI Layer                                                    │
│  ├── MainActivity (NFC detection + navigation)              │
│  ├── EncryptActivity (file encryption UI)                   │
│  ├── DecryptActivity (file decryption UI)                   │
│  └── CardManagementActivity (card operations)               │
├─────────────────────────────────────────────────────────────┤
│  Business Logic                                              │
│  ├── FileEncryptor (encryption orchestration)               │
│  ├── FileDecryptor (decryption orchestration)               │
│  └── CardManager (card management)                          │
├─────────────────────────────────────────────────────────────┤
│  Crypto Layer (BouncyCastle)                                │
│  ├── RSAEncryption (RSA-2048 + PKCS#1 v1.5)                │
│  └── AESEncryption (AES-256-GCM)                            │
├─────────────────────────────────────────────────────────────┤
│  APDU Layer                                                  │
│  ├── OpenPGPCard (OpenPGP commands)                         │
│  ├── APDUCommand (command builder)                          │
│  └── APDUResponse (response parser)                         │
├─────────────────────────────────────────────────────────────┤
│  NFC Layer (Android NFC API)                                │
│  ├── NFCCardManager (NFC detection + connection)            │
│  ├── IsoDepConnection (IsoDep wrapper)                      │
│  └── CardReader (card discovery)                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│         Android NFC API (Built-in)                          │
│  android.nfc.tech.IsoDep                                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│         NFC Radio (Hardware)                                 │
│  13.56 MHz, ISO 14443-4                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│         AEPGP Smart Card (NFC-enabled)                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Implementation Files

### NFC Layer

#### `NFCCardManager.kt`
```kotlin
class NFCCardManager(private val activity: Activity) {
    private val nfcAdapter: NfcAdapter? = NfcAdapter.getDefaultAdapter(activity)

    fun enableForegroundDispatch() {
        // Enable foreground NFC dispatch to capture card taps
    }

    fun disableForegroundDispatch() {
        // Disable when activity pauses
    }

    fun handleIntent(intent: Intent): IsoDep? {
        // Extract IsoDep tag from NFC intent
        val tag = intent.getParcelableExtra<Tag>(NfcAdapter.EXTRA_TAG)
        return IsoDep.get(tag)
    }
}
```

#### `IsoDepConnection.kt`
```kotlin
class IsoDepConnection(private val isoDep: IsoDep) {
    fun connect() {
        isoDep.connect()
        isoDep.timeout = 5000 // 5 second timeout
    }

    fun transceive(apdu: ByteArray): ByteArray {
        return isoDep.transceive(apdu)
    }

    fun close() {
        isoDep.close()
    }
}
```

### APDU Layer

#### `OpenPGPCard.kt`
```kotlin
class OpenPGPCard(private val connection: IsoDepConnection) {

    fun selectApplet(): Boolean {
        // SELECT OpenPGP applet: 00 A4 04 00 06 D2 76 00 01 24 01
        val apdu = byteArrayOf(
            0x00, 0xA4.toByte(), 0x04, 0x00, 0x06,
            0xD2.toByte(), 0x76, 0x00, 0x01, 0x24, 0x01
        )
        val response = connection.transceive(apdu)
        return isSuccess(response)
    }

    fun verifyPIN(pin: String): Boolean {
        // VERIFY PIN: 00 20 00 82 [Lc] [PIN]
        val pinBytes = pin.toByteArray()
        val apdu = byteArrayOf(0x00, 0x20, 0x00, 0x82.toByte(), pinBytes.size.toByte()) + pinBytes
        val response = connection.transceive(apdu)
        return isSuccess(response)
    }

    fun getPublicKey(): ByteArray? {
        // GET PUBLIC KEY: 00 47 81 00 02 B8 00 00
        val apdu = byteArrayOf(0x00, 0x47, 0x81.toByte(), 0x00, 0x02, 0xB8.toByte(), 0x00, 0x00)
        val response = connection.transceive(apdu)

        // Handle GET RESPONSE if needed (SW=61XX)
        var fullResponse = response
        if (response.size >= 2 && response[response.size - 2] == 0x61.toByte()) {
            val remainingBytes = response[response.size - 1].toInt() and 0xFF
            val getResponseApdu = byteArrayOf(0x00, 0xC0.toByte(), 0x00, 0x00, remainingBytes.toByte())
            fullResponse = connection.transceive(getResponseApdu)
        }

        return if (isSuccess(fullResponse)) {
            fullResponse.copyOfRange(0, fullResponse.size - 2)
        } else null
    }

    fun decrypt(encryptedData: ByteArray): ByteArray? {
        // PSO:DECIPHER: 00 2A 80 86 [data]
        val apdu = byteArrayOf(0x00, 0x2A, 0x80.toByte(), 0x86.toByte()) +
                    encryptedData.size.toByte() +
                    byteArrayOf(0x00) +  // Padding indicator
                    encryptedData +
                    byteArrayOf(0x00)    // Le
        val response = connection.transceive(apdu)
        return if (isSuccess(response)) {
            response.copyOfRange(0, response.size - 2)
        } else null
    }

    private fun isSuccess(response: ByteArray): Boolean {
        return response.size >= 2 &&
               response[response.size - 2] == 0x90.toByte() &&
               response[response.size - 1] == 0x00.toByte()
    }
}
```

---

## Implementation Phases (Updated for NFC)

### ✅ Phase 1: Project Setup (COMPLETE)
- [x] Android project structure
- [x] Gradle configuration
- [x] AndroidManifest with NFC permissions
- [x] NFC tech filter XML

### Phase 2: NFC Communication (NEXT)
- [ ] Implement `NFCCardManager` - NFC detection and foreground dispatch
- [ ] Implement `IsoDepConnection` - IsoDep wrapper
- [ ] Implement card discovery and connection
- [ ] Test NFC with real card

### Phase 3: APDU Layer
- [ ] Implement `OpenPGPCard` - OpenPGP commands via NFC
- [ ] Implement SELECT, VERIFY, GET PUBLIC KEY
- [ ] Implement PSO:DECIPHER
- [ ] Test APDU commands

### Phase 4-8: Same as original plan
(Crypto, Business Logic, UI, Card Management, Testing, Release)

---

## NFC User Flow

### Encryption Flow

1. **User opens app** → MainActivity shown
2. **User taps "Encrypt File"** → EncryptActivity shown
3. **User selects file** → File picker opens
4. **User taps card to phone** → NFC discovers card
5. **App connects** → IsoDep connection established
6. **App reads public key** → GET PUBLIC KEY command
7. **App encrypts file** → RSA+AES encryption
8. **App saves .enc file** → File created
9. **Success dialog shown**

**Total time**: ~5-10 seconds (including NFC tap)

### Decryption Flow

1. **User opens app** → MainActivity shown
2. **User taps "Decrypt File"** → DecryptActivity shown
3. **User selects .enc file** → File picker opens
4. **User taps card to phone** → NFC discovers card
5. **App connects** → IsoDep connection established
6. **PIN dialog shown** → User enters PIN
7. **App verifies PIN** → VERIFY PIN command
8. **App decrypts AES key** → PSO:DECIPHER command
9. **App decrypts file** → AES-GCM decryption
10. **App saves decrypted file** → Original file restored
11. **Success dialog shown**

**Total time**: ~5-15 seconds (including NFC tap + PIN entry)

---

## Advantages of NFC Implementation

### For Users
✅ **No accessories needed** - Works with phone's built-in NFC
✅ **Simpler operation** - Just tap card to phone
✅ **Faster** - No cables to connect
✅ **More portable** - Carry just phone and card
✅ **Works anywhere** - No desk or surface needed
✅ **Lower cost** - No card reader to buy

### For Developers
✅ **Simpler code** - Android NFC API is straightforward
✅ **No USB complexity** - No CCID protocol implementation
✅ **Better debugging** - Easier to test
✅ **More devices supported** - Most Android phones have NFC
✅ **Fewer permissions** - No USB permissions complexity
✅ **Better battery life** - NFC uses less power

### For Deployment
✅ **Wider compatibility** - 90%+ of Android phones
✅ **No hardware dependencies** - Works out of the box
✅ **Easier testing** - Just need NFC-enabled phone
✅ **Better user experience** - Tap is intuitive
✅ **Lower support burden** - Fewer setup issues

---

## Testing NFC Implementation

### Prerequisites for Testing
- Android device with NFC (most modern phones)
- AEPGP smart card with NFC chip
- Enable NFC in phone settings

### Test Checklist
- [ ] NFC detection works when card tapped
- [ ] IsoDep connection established
- [ ] SELECT applet command works
- [ ] GET PUBLIC KEY works
- [ ] VERIFY PIN works
- [ ] PSO:DECIPHER works
- [ ] File encryption works
- [ ] File decryption works
- [ ] Cross-platform compatibility (encrypt on Android, decrypt on Windows/macOS)
- [ ] Error handling (card removed, wrong PIN, etc.)

### Testing Tools
```kotlin
// Enable NFC debugging
adb shell settings put global nfc_debug_enabled 1

// View NFC logs
adb logcat -s NfcService,NfcDispatcher,IsoDep
```

---

## Known Limitations of NFC

### Technical Limitations
1. **Card must stay near phone** - Must maintain < 4cm distance during operation
2. **Can be slower for long operations** - Key generation may timeout
3. **NFC hardware varies** - Some phones have weaker/stronger NFC
4. **Metal cases interfere** - May need to remove phone case

### Mitigation Strategies
1. **Progress indicators** - Show "Keep card near phone" message
2. **Timeout handling** - Gracefully handle NFC timeouts
3. **Card detection feedback** - Vibrate/sound when card detected
4. **Clear instructions** - Guide user to keep card close

---

## Next Steps

### Immediate (Phase 2)
1. Create `NFCCardManager.kt` - NFC detection
2. Create `IsoDepConnection.kt` - Connection wrapper
3. Implement foreground dispatch
4. Test with real NFC card

### Short-term (Phase 3)
1. Create `OpenPGPCard.kt` - APDU commands
2. Implement all OpenPGP card operations
3. Test APDU communication
4. Handle errors and edge cases

### Medium-term (Phases 4-6)
1. Implement crypto (RSA+AES)
2. Implement business logic
3. Create UI activities
4. Implement card management

### Long-term (Phases 7-8)
1. Comprehensive testing
2. Performance optimization
3. Create release build
4. Publish to Play Store (optional)

---

## Resources

### Android NFC Documentation
- NFC Basics: https://developer.android.com/guide/topics/connectivity/nfc/nfc
- IsoDep: https://developer.android.com/reference/android/nfc/tech/IsoDep
- Advanced NFC: https://developer.android.com/guide/topics/connectivity/nfc/advanced-nfc

### OpenPGP Card
- Specification: https://g10code.com/docs/openpgp-card-2.0.pdf
- Commands: https://github.com/ANSSI-FR/SmartPGP

### Similar Projects
- OpenKeychain (Android OpenPGP with NFC): https://github.com/open-keychain/open-keychain
- NFC Tools: https://github.com/nfctools

---

## Summary

**NFC is the right choice for Android AEPGP implementation** because:

1. ✅ Built into most Android phones (no extra hardware)
2. ✅ Simpler implementation (native Android API)
3. ✅ Better user experience (just tap card)
4. ✅ More portable (no cables/adapters)
5. ✅ Wider device compatibility
6. ✅ Easier to test and debug

**Status**: Project structure updated for NFC, ready for Phase 2 implementation.

**Recommendation**: Proceed with NFC implementation. USB OTG can be added later as an optional alternative for devices without NFC (rare).
