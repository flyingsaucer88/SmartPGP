# AEPGP Android Encryptor

**Version**: 1.0.0
**Platform**: Android 8.0+ (API 26+)

Native Android application for encrypting and decrypting files using AEPGP smart card via USB OTG.

---

## Overview

AEPGP Android Encryptor provides seamless file encryption and decryption on Android devices using your AEPGP smart card connected via USB OTG. The app uses the same RSA-2048 + AES-256-GCM hybrid encryption as Windows and macOS versions, ensuring full cross-platform compatibility.

### Key Features

- ✅ **USB OTG Support** - Connect AEPGP card reader via USB OTG
- ✅ **File Encryption** - Encrypt files with RSA-2048 + AES-256-GCM
- ✅ **File Decryption** - Decrypt files with card's private key
- ✅ **Card Management** - Generate keys, change PIN, factory reset
- ✅ **Cross-Platform Compatible** - Same format as Windows/macOS
- ✅ **Material Design** - Modern Android UI
- ✅ **Scoped Storage** - Android 10+ storage access

---

## System Requirements

### Hardware
- **Android Device** with USB OTG support
- **AEPGP Smart Card** (AmbiSecure token)
  - ATR: `3B D5 18 FF 81 B1 FE 45 1F C3 80 73 C8 21 10 6F`
- **USB Smart Card Reader** (USB-A or USB-C)
- **OTG Adapter** (if needed for USB-A readers)

### Software
- **Android 8.0+** (API 26+)
- USB Host API support
- Minimum 50MB free storage

---

## Features

### File Operations
1. **Encrypt Files**
   - Browse and select file from device storage
   - Card encrypts with RSA-2048 + AES-256-GCM
   - Creates .enc file in same directory
   - No file size limit (streaming encryption)

2. **Decrypt Files**
   - Browse and select .enc file
   - Enter PIN when prompted
   - Card decrypts using private key
   - Restores original filename

### Card Management
1. **Generate Keypair**
   - Generate RSA-2048 keys on card
   - Takes 30-120 seconds
   - Requires admin PIN

2. **Change PIN**
   - Update user PIN (6-127 characters)
   - Secure PIN entry dialog
   - Verification required

3. **Factory Reset**
   - Delete all keys from card
   - Reset PINs to defaults
   - Requires confirmation

### Security Features
- Private keys never leave the card
- PIN-protected decryption
- Card lockout after 3 failed attempts
- Hardware-backed encryption
- ATR verification (AmbiSecure tokens only)

---

## Installation

### From APK
1. Download `AEPGPEncryptor-v1.0.0.apk`
2. Enable "Install from Unknown Sources" in Settings
3. Install the APK
4. Grant necessary permissions

### Build from Source
```bash
cd android_app/AEPGPEncryptor
./gradlew assembleRelease
# APK in: app/build/outputs/apk/release/
```

### Permissions Required
- **USB Host** - Access USB smart card reader
- **Storage** - Read/write encrypted files
- **Foreground Service** - Keep card connection alive

---

## Usage

### First Time Setup

1. **Connect Card Reader**
   - Plug USB card reader into OTG adapter
   - Insert AEPGP card
   - Connect to Android device
   - App should detect reader automatically

2. **Generate Keys** (if first time)
   - Open app
   - Tap "Card Management"
   - Tap "Generate Keys"
   - Confirm generation
   - Wait 30-120 seconds
   - Default PIN: `123456`

### Encrypting a File

1. Launch AEPGP Encryptor app
2. Tap **"Encrypt File"**
3. Browse and select file
4. Wait for encryption
5. Encrypted file created with `.enc` extension
6. Share or backup encrypted file

### Decrypting a File

1. Launch AEPGP Encryptor app
2. Tap **"Decrypt File"**
3. Browse and select `.enc` file
4. Enter PIN when prompted
5. Wait for decryption
6. Original file restored

### Changing PIN

1. Tap **"Card Management"**
2. Tap **"Change PIN"**
3. Enter current PIN (default: `123456`)
4. Enter new PIN (6-127 chars)
5. Confirm new PIN
6. Success message shown

---

## Technical Details

### Architecture

**Components**:
1. **UsbManager** - Android USB Host API for reader detection
2. **SmartCardIO** - PC/SC-like API for Android
3. **APDU Layer** - OpenPGP card communication
4. **Crypto Module** - RSA+AES hybrid encryption
5. **Storage Access Framework** - File picking and management

**Libraries Used**:
- `usb-serial-for-android` or `smartcard-api` - USB smart card communication
- BouncyCastle - Cryptography (RSA, AES-GCM)
- AndroidX - Modern Android components
- Material Components - UI

### APDU Commands

Same commands as Windows/macOS versions:

| Command | Description |
|---------|-------------|
| `00 A4 04 00 06 D2 76 00 01 24 01` | SELECT OpenPGP applet |
| `00 47 81 00 02 B8 00` | GET PUBLIC KEY |
| `00 20 00 82 [Lc] [PIN]` | VERIFY PIN |
| `00 2A 80 86 [data]` | PSO:DECIPHER |

### Encryption Format

Identical to Windows/macOS for full compatibility:

```
[4 bytes: encrypted AES key length (big-endian)]
[256 bytes: RSA-encrypted AES-256 key]
[12 bytes: IV for AES-GCM]
[16 bytes: GCM authentication tag]
[remaining: AES-256-GCM encrypted file data]
```

### Supported Card Readers

Tested with:
- **Generic USB CCID readers**
- **ACS ACR38U** series
- **Identiv uTrust** series
- **Gemalto PC Twin** readers

Requirements:
- USB CCID compliant
- Compatible with Android USB Host API
- Supports ISO 7816 smart cards

---

## Cross-Platform Compatibility

### File Format Compatibility
- ✅ Files encrypted on Android decrypt on Windows
- ✅ Files encrypted on Android decrypt on macOS
- ✅ Files encrypted on Windows/macOS decrypt on Android
- ✅ Same RSA-2048 + AES-256-GCM algorithms
- ✅ Same .enc file extension

### Testing Matrix

| Encrypt On | Decrypt On | Status |
|------------|------------|--------|
| Android | Android | ✅ Works |
| Android | Windows | ✅ Works |
| Android | macOS | ✅ Works |
| Windows | Android | ✅ Works |
| macOS | Android | ✅ Works |

---

## Troubleshooting

### Card Reader Not Detected

**Problem**: App doesn't detect USB card reader

**Solutions**:
- ✅ Check device has USB OTG support
- ✅ Test OTG adapter with USB drive
- ✅ Ensure card reader is USB CCID compliant
- ✅ Try different USB port/adapter
- ✅ Restart app after connecting reader

### "AEPGP card not found"

**Problem**: App detects reader but not card

**Solutions**:
- ✅ Ensure card is properly inserted
- ✅ Try removing and reinserting card
- ✅ Check card ATR in app settings
- ✅ Verify card is AmbiSecure AEPGP token

### "No keys on card"

**Problem**: Card doesn't have encryption keys

**Solutions**:
- Generate keys: Card Management → Generate Keys
- Use default Admin PIN: `12345678`
- Wait 30-120 seconds for generation

### "Wrong PIN"

**Problem**: Incorrect PIN entered

**Solutions**:
- Default PIN: `123456`
- Check caps lock/number pad
- After 3 failures, card locks
- Use Admin PIN to unlock if needed

### Permission Denied

**Problem**: Can't access files or USB

**Solutions**:
- Grant all requested permissions
- Enable USB debugging for some devices
- Check scoped storage settings (Android 10+)

---

## Security Considerations

### What's Secure
- ✅ Private keys never leave smart card
- ✅ PIN-protected decryption operations
- ✅ Hardware-backed encryption
- ✅ GCM authenticated encryption
- ✅ ATR verification (AmbiSecure only)

### What's NOT Secure
- ⚠️ PIN entered on device keyboard (visible in memory)
- ⚠️ Encrypted files stored on device (physical access risk)
- ⚠️ USB OTG connection not encrypted
- ⚠️ App runs without sandbox isolation

### Best Practices
1. Use strong PIN (not default `123456`)
2. Don't leave card in reader when not in use
3. Keep encrypted files on removable storage
4. Regularly backup encrypted files
5. Update app for security patches

---

## Development

### Project Structure

```
android_app/AEPGPEncryptor/
├── app/
│   ├── src/main/
│   │   ├── java/com/aepgp/encryptor/
│   │   │   ├── MainActivity.kt
│   │   │   ├── EncryptActivity.kt
│   │   │   ├── DecryptActivity.kt
│   │   │   ├── CardManagementActivity.kt
│   │   │   ├── usb/
│   │   │   │   ├── UsbCardManager.kt
│   │   │   │   └── SmartCardConnection.kt
│   │   │   ├── crypto/
│   │   │   │   ├── AEPGPCrypto.kt
│   │   │   │   ├── RSAEncryption.kt
│   │   │   │   └── AESEncryption.kt
│   │   │   ├── apdu/
│   │   │   │   ├── APDUCommand.kt
│   │   │   │   └── OpenPGPCard.kt
│   │   │   └── utils/
│   │   │       ├── FileUtils.kt
│   │   │       └── CardUtils.kt
│   │   ├── res/
│   │   │   ├── layout/
│   │   │   │   ├── activity_main.xml
│   │   │   │   ├── activity_encrypt.xml
│   │   │   │   ├── activity_decrypt.xml
│   │   │   │   └── dialog_pin_entry.xml
│   │   │   ├── values/
│   │   │   │   ├── strings.xml
│   │   │   │   ├── colors.xml
│   │   │   │   └── themes.xml
│   │   │   └── drawable/
│   │   └── AndroidManifest.xml
│   └── build.gradle
├── build.gradle
├── settings.gradle
└── README.md
```

### Building

```bash
# Debug build
./gradlew assembleDebug

# Release build
./gradlew assembleRelease

# Install to device
./gradlew installDebug

# Run tests
./gradlew test
```

### Testing

1. **Unit Tests** - Crypto and APDU logic
2. **Instrumented Tests** - UI and file operations
3. **Manual Testing** - Real card reader and card

---

## Version History

### Version 1.0.0 (2026-01-05)
- ✨ Initial release
- ✅ File encryption/decryption
- ✅ USB OTG smart card reader support
- ✅ Card management (generate, change PIN, reset)
- ✅ Material Design UI
- ✅ Cross-platform file format compatibility
- ✅ Android 8.0+ support

---

## License

Based on **SmartPGP** project by ANSSI (French National Cybersecurity Agency)

**License**: GNU General Public License v2 (GPL v2)

**Original Project**: https://github.com/ANSSI-FR/SmartPGP

---

## Support & Credits

### Credits
- **SmartPGP JavaCard Implementation**: ANSSI
- **Android Development**: AEPGP team
- **Cryptography**: BouncyCastle library

### Support
For issues and support:
- Check this documentation
- Review app logs
- Contact AEPGP administrator

---

**AEPGP Android Encryptor v1.0.0 - Secure File Encryption on Android with Smart Cards**
