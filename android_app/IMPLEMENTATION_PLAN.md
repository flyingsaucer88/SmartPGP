# AEPGP Android App - Implementation Plan

**Date**: 2026-01-05
**Branch**: Androidgpg
**Status**: 🚧 In Progress - Initial Structure Created

---

## Overview

Android application for encrypting and decrypting files using AEPGP smart card via USB OTG. The app will provide the same RSA-2048 + AES-256-GCM encryption as Windows and macOS versions, with full cross-platform file format compatibility.

---

## Requirements

### Functional Requirements

#### File Operations
- **FR1**: Encrypt files using AEPGP card via USB OTG
- **FR2**: Decrypt .enc files using card's private key
- **FR3**: Support all file types and sizes (streaming encryption)
- **FR4**: Maintain same encryption format as Windows/macOS
- **FR5**: Create .enc files in same directory as source

#### Card Management
- **FR6**: Detect and connect to USB smart card reader
- **FR7**: Verify AEPGP card by ATR
- **FR8**: Generate RSA-2048 keypair on card
- **FR9**: Change user PIN (6-127 characters)
- **FR10**: Factory reset (delete all keys)

#### User Interface
- **FR11**: Material Design UI following Android guidelines
- **FR12**: File picker for selecting files
- **FR13**: Progress indicators for long operations
- **FR14**: Error handling with user-friendly messages
- **FR15**: Card status display

### Non-Functional Requirements

#### Performance
- **NFR1**: Encryption/decryption should use streaming to handle large files
- **NFR2**: UI should remain responsive during operations
- **NFR3**: Card operations should have timeout handling

#### Security
- **NFR4**: Private keys never leave the smart card
- **NFR5**: PIN entry via secure input dialog
- **NFR6**: Only accept AmbiSecure AEPGP tokens (ATR check)
- **NFR7**: No logging of sensitive data (PINs, keys)

#### Compatibility
- **NFR8**: Support Android 8.0+ (API 26+)
- **NFR9**: Work with USB CCID card readers
- **NFR10**: Files encrypted on Android decrypt on Windows/macOS
- **NFR11**: Files encrypted on Windows/macOS decrypt on Android

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Android Application                     │
├─────────────────────────────────────────────────────────────┤
│  UI Layer (Activities/Fragments)                            │
│  ├── MainActivity (navigation)                              │
│  ├── EncryptActivity (file encryption UI)                   │
│  ├── DecryptActivity (file decryption UI)                   │
│  └── CardManagementActivity (card operations UI)            │
├─────────────────────────────────────────────────────────────┤
│  Business Logic Layer                                        │
│  ├── FileEncryptor (encryption orchestration)               │
│  ├── FileDecryptor (decryption orchestration)               │
│  └── CardManager (card management operations)               │
├─────────────────────────────────────────────────────────────┤
│  Crypto Layer                                                │
│  ├── AEPGPCrypto (main crypto interface)                    │
│  ├── RSAEncryption (RSA key handling, BouncyCastle)         │
│  └── AESEncryption (AES-GCM encryption, BouncyCastle)       │
├─────────────────────────────────────────────────────────────┤
│  APDU Layer                                                  │
│  ├── OpenPGPCard (OpenPGP card commands)                    │
│  ├── APDUCommand (APDU command builder)                     │
│  └── APDUResponse (APDU response parser)                    │
├─────────────────────────────────────────────────────────────┤
│  USB Layer                                                   │
│  ├── UsbCardManager (USB device management)                 │
│  ├── SmartCardConnection (card connection wrapper)          │
│  └── CardReader (reader detection and init)                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│         Android USB Host API                                 │
│  (UsbManager, UsbDevice, UsbDeviceConnection)               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│         USB Smart Card Reader (CCID)                        │
│  (Connected via USB OTG)                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│         AEPGP Smart Card                                     │
│  (AmbiSecure Token)                                          │
└─────────────────────────────────────────────────────────────┘
```

### Package Structure

```
com.aepgp.encryptor/
├── MainActivity.kt
├── EncryptActivity.kt
├── DecryptActivity.kt
├── CardManagementActivity.kt
├── usb/
│   ├── UsbCardManager.kt
│   ├── SmartCardConnection.kt
│   ├── CardReader.kt
│   └── UsbPermissionHelper.kt
├── apdu/
│   ├── OpenPGPCard.kt
│   ├── APDUCommand.kt
│   ├── APDUResponse.kt
│   └── CardConstants.kt
├── crypto/
│   ├── AEPGPCrypto.kt
│   ├── RSAEncryption.kt
│   ├── AESEncryption.kt
│   └── CryptoUtils.kt
├── business/
│   ├── FileEncryptor.kt
│   ├── FileDecryptor.kt
│   └── CardManager.kt
├── ui/
│   ├── dialogs/
│   │   ├── PinEntryDialog.kt
│   │   ├── ProgressDialog.kt
│   │   └── ErrorDialog.kt
│   └── adapters/
│       └── FileListAdapter.kt
└── utils/
    ├── FileUtils.kt
    ├── CardUtils.kt
    ├── ByteUtils.kt
    └── Logger.kt
```

---

## Implementation Phases

### Phase 1: Project Setup & USB Communication ✅ STARTED
- [x] Create Android project structure
- [x] Configure Gradle dependencies
- [x] Create AndroidManifest.xml
- [ ] Implement USB permission handling
- [ ] Implement USB device detection
- [ ] Test USB connection with card reader

### Phase 2: APDU Communication Layer
- [ ] Implement APDUCommand builder
- [ ] Implement APDUResponse parser
- [ ] Implement OpenPGPCard class
- [ ] Implement SELECT applet command
- [ ] Implement VERIFY PIN command
- [ ] Implement GET PUBLIC KEY command
- [ ] Implement PSO:DECIPHER command
- [ ] Test APDU communication with real card

### Phase 3: Cryptography Module
- [ ] Implement RSA public key reading
- [ ] Implement RSA encryption (BouncyCastle)
- [ ] Implement AES-256-GCM encryption
- [ ] Implement AES-256-GCM decryption
- [ ] Implement file format writing
- [ ] Implement file format reading
- [ ] Test encryption/decryption locally

### Phase 4: Business Logic
- [ ] Implement FileEncryptor class
- [ ] Implement FileDecryptor class
- [ ] Implement CardManager class
- [ ] Implement streaming encryption for large files
- [ ] Implement progress tracking
- [ ] Add error handling and recovery

### Phase 5: User Interface
- [ ] Design MainActivity layout
- [ ] Implement MainActivity navigation
- [ ] Design EncryptActivity layout
- [ ] Implement file picker integration
- [ ] Design DecryptActivity layout
- [ ] Implement PIN entry dialog
- [ ] Design CardManagementActivity layout
- [ ] Implement progress indicators
- [ ] Add Material Design styling

### Phase 6: Card Management Features
- [ ] Implement key generation via GPG (if possible)
- [ ] Or implement direct APDU key generation
- [ ] Implement PIN change functionality
- [ ] Implement factory reset functionality
- [ ] Test all card management operations

### Phase 7: Testing & Polish
- [ ] Unit tests for crypto module
- [ ] Unit tests for APDU layer
- [ ] Integration tests with mock card
- [ ] Manual testing with real card
- [ ] Cross-platform compatibility testing
- [ ] Performance optimization
- [ ] UI/UX improvements
- [ ] Documentation

### Phase 8: Release Preparation
- [ ] Code review and cleanup
- [ ] ProGuard configuration
- [ ] APK signing configuration
- [ ] Create release build
- [ ] User documentation
- [ ] Developer documentation

---

## Technical Challenges

### Challenge 1: USB Communication

**Problem**: Android USB Host API is low-level, need to implement CCID protocol

**Solutions**:
1. Use existing library like `usb-serial-for-android` (partial support)
2. Implement CCID protocol manually
3. Use SEEK for Android if available (deprecated)

**Chosen**: Implement CCID protocol manually using Android USB Host API

### Challenge 2: Key Generation

**Problem**: GPG not available on Android for automated card management

**Solutions**:
1. Implement direct APDU key generation commands
2. Guide user through manual GPG setup (requires root/terminal)
3. Pre-generate keys and expect user to have keys already

**Chosen**: Implement direct APDU key generation (same as Windows v1.3.1)

### Challenge 3: Large File Handling

**Problem**: Android has memory constraints, can't load entire file

**Solutions**:
1. Streaming encryption with buffered I/O
2. Chunked processing
3. File size limits

**Chosen**: Streaming encryption with 64KB buffers

### Challenge 4: Storage Access

**Problem**: Android 10+ scoped storage restrictions

**Solutions**:
1. Use Storage Access Framework (SAF)
2. Request MANAGE_EXTERNAL_STORAGE permission
3. Save to app-specific directory

**Chosen**: Use SAF for file picking, save encrypted files to same directory as source

---

## Dependencies

### Core Dependencies
- **AndroidX Core**: Latest stable (androidx.core:core-ktx)
- **AndroidX AppCompat**: For compatibility
- **Material Components**: UI components
- **Kotlin Coroutines**: Async operations

### USB & Smart Card
- **USB Serial for Android**: USB communication helper
- Alternative: Direct Android USB Host API

### Cryptography
- **BouncyCastle**: RSA and AES-GCM (bcprov-jdk15on, bcpkix-jdk15on)

### File Operations
- **DocumentFile**: Storage Access Framework support

---

## Encryption Format (Same as Windows/macOS)

```
File Structure:
┌────────────────────────────────────────────┐
│ 4 bytes: Encrypted AES Key Length         │
│          (big-endian uint32)               │
├────────────────────────────────────────────┤
│ 256 bytes: RSA-Encrypted AES-256 Key      │
│            (PKCS#1 v1.5 padding)           │
├────────────────────────────────────────────┤
│ 12 bytes: AES-GCM IV                       │
│           (random)                         │
├────────────────────────────────────────────┤
│ 16 bytes: GCM Authentication Tag          │
├────────────────────────────────────────────┤
│ Remaining: AES-256-GCM Encrypted Data     │
│            (variable length)               │
└────────────────────────────────────────────┘
```

### Algorithms
- **RSA**: 2048-bit with PKCS#1 v1.5 padding
- **AES**: 256-bit key with GCM mode
- **IV**: 12 bytes (96 bits) for GCM
- **Auth Tag**: 16 bytes (128 bits)

---

## Testing Strategy

### Unit Tests
1. APDU command building/parsing
2. RSA encryption/decryption
3. AES-GCM encryption/decryption
4. File format writing/reading
5. Byte array utilities

### Integration Tests
1. USB device detection
2. Card connection
3. APDU command execution
4. Full encryption workflow
5. Full decryption workflow

### Manual Tests
1. Encrypt file on Android, decrypt on Windows
2. Encrypt file on Windows, decrypt on Android
3. Encrypt file on Android, decrypt on macOS
4. Large file encryption (>100MB)
5. Multiple file operations
6. Card removal during operation
7. PIN entry failure scenarios

---

## Security Considerations

### What We Control
✅ RSA and AES implementation (BouncyCastle)
✅ APDU communication security
✅ ATR verification (AmbiSecure only)
✅ No logging of sensitive data

### What We Don't Control
⚠️ Android USB stack security
⚠️ Device physical security
⚠️ User's PIN choice
⚠️ Encrypted file storage location

### Best Practices
1. Use strong cryptographic libraries (BouncyCastle)
2. Verify card ATR before operations
3. Clear sensitive data from memory after use
4. Use secure PIN entry (no echo)
5. Implement timeout for card operations
6. Warn user about using default PIN

---

## Current Status

### ✅ Completed
- Project structure created
- Gradle configuration
- Dependencies defined
- README documentation
- Implementation plan

### 🚧 In Progress
- AndroidManifest.xml
- USB permission handling

### ⏳ Pending
- All implementation phases (2-8)
- Testing
- Release preparation

---

## Next Steps

1. Complete AndroidManifest.xml and XML resources
2. Implement USB layer (UsbCardManager, SmartCardConnection)
3. Implement APDU layer (OpenPGPCard, APDUCommand)
4. Implement crypto layer (RSAEncryption, AESEncryption)
5. Implement business logic (FileEncryptor, FileDecryptor)
6. Implement UI activities
7. Test with real hardware
8. Create release build

---

## Timeline Estimate

**Note**: This is a complex Android app requiring extensive testing with hardware.

- Phase 1 (USB): 2-3 days
- Phase 2 (APDU): 2-3 days
- Phase 3 (Crypto): 2-3 days
- Phase 4 (Business Logic): 2-3 days
- Phase 5 (UI): 3-4 days
- Phase 6 (Card Mgmt): 2-3 days
- Phase 7 (Testing): 3-5 days
- Phase 8 (Release): 1-2 days

**Total Estimated**: 17-26 days of focused development

---

## Resources

### Documentation
- Android USB Host API: https://developer.android.com/guide/topics/connectivity/usb/host
- OpenPGP Card Specification: https://g10code.com/docs/openpgp-card-2.0.pdf
- BouncyCastle Crypto: https://www.bouncycastle.org/documentation.html
- Material Design: https://material.io/design

### Similar Projects
- OpenKeychain (Android OpenPGP implementation)
- Smart Card API for Android (deprecated but reference)
- PC/SC Smart Card Reader implementations

---

**Status**: Initial project structure created, ready for implementation.

**Next Task**: Implement USB communication layer and APDU commands.
