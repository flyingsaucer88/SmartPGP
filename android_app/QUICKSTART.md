# AEPGP Android - Quick Start Guide

## Project Status

🚧 **IN DEVELOPMENT** - Initial project structure created

This Android application is currently under development. The project structure and build configuration are complete, but implementation is in progress.

---

## What's Included

### ✅ Completed
- Android project structure
- Gradle build configuration
- Dependencies configuration (BouncyCastle, USB, AndroidX)
- README documentation
- Implementation plan
- Project architecture design

### 🚧 In Progress
- USB smart card reader communication
- APDU command layer
- Cryptography module
- User interface
- File encryption/decryption logic

---

## Requirements for Development

### Hardware
- Android device with USB OTG support
- AEPGP smart card (AmbiSecure token)
- USB smart card reader (CCID compatible)
- USB OTG cable/adapter

### Software
- Android Studio Hedgehog (2023.1.1) or later
- Android SDK API 34
- Gradle 8.1+
- Kotlin 1.9+

---

## Building the Project

### 1. Clone Repository
```bash
cd /path/to/SmartPGP
git checkout Androidgpg
```

### 2. Open in Android Studio
```
File → Open → Select: android_app/AEPGPEncryptor
```

### 3. Sync Gradle
Android Studio will automatically sync Gradle dependencies.

### 4. Build
```bash
# From Android Studio
Build → Make Project

# Or from command line
cd android_app/AEPGPEncryptor
./gradlew assembleDebug
```

### 5. Run on Device
```bash
# Connect Android device via USB
# Enable USB debugging
./gradlew installDebug
```

---

## Project Structure

```
android_app/
├── AEPGPEncryptor/          # Main Android project
│   ├── app/
│   │   ├── src/main/
│   │   │   ├── java/com/aepgp/encryptor/  # Source code (TBD)
│   │   │   ├── res/                        # Resources (TBD)
│   │   │   └── AndroidManifest.xml         # Manifest (TBD)
│   │   └── build.gradle                    # App build config ✅
│   ├── build.gradle                        # Project build config ✅
│   ├── settings.gradle                     # Gradle settings ✅
│   └── README.md                           # App documentation ✅
├── IMPLEMENTATION_PLAN.md   # Detailed implementation plan ✅
└── QUICKSTART.md           # This file ✅
```

---

## Dependencies

### Core Android
- AndroidX Core KTX 1.12.0
- AppCompat 1.6.1
- Material Components 1.11.0
- ConstraintLayout 2.1.4

### USB & Smart Card
- USB Serial for Android 3.7.0
- (Future: Custom CCID implementation)

### Cryptography
- BouncyCastle Provider 1.70
- BouncyCastle PKIX 1.70

### Utilities
- Kotlin Coroutines 1.7.3
- Lifecycle Components 2.7.0
- DocumentFile 1.0.1

---

## Next Steps for Developers

### Phase 1: USB Communication
1. Implement `UsbCardManager.kt` - USB device detection
2. Implement `SmartCardConnection.kt` - Card reader connection
3. Implement CCID protocol for smart card communication
4. Test with real USB card reader

### Phase 2: APDU Layer
1. Implement `APDUCommand.kt` - APDU command builder
2. Implement `APDUResponse.kt` - APDU response parser
3. Implement `OpenPGPCard.kt` - OpenPGP card operations
4. Test with real AEPGP card

### Phase 3: Cryptography
1. Implement RSA public key reading from card
2. Implement AES-256-GCM encryption
3. Implement file format (compatible with Windows/macOS)
4. Test encryption/decryption

### Phase 4: UI & Business Logic
1. Create MainActivity with navigation
2. Create EncryptActivity for file encryption
3. Create DecryptActivity for file decryption
4. Implement file picker integration
5. Add progress indicators and error handling

---

## Testing

### Unit Tests
```bash
./gradlew test
```

### Instrumented Tests (on device/emulator)
```bash
./gradlew connectedAndroidTest
```

### Manual Testing
Will require:
- Real Android device with USB OTG
- AEPGP smart card
- USB card reader
- Test files for encryption/decryption

---

## Known Limitations

### Current Limitations
- ⚠️ No implementation yet - project structure only
- ⚠️ Requires hardware for testing (card reader + card)
- ⚠️ Complex USB communication layer needed
- ⚠️ Key generation may require direct APDU implementation

### Future Limitations
- Android 8.0+ only (API 26+)
- Requires USB OTG support
- CCID-compatible card readers only
- May not work on all Android devices
- Performance depends on device hardware

---

## Resources

### Documentation
- [README.md](AEPGPEncryptor/README.md) - Full app documentation
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Detailed implementation plan
- Android USB Host: https://developer.android.com/guide/topics/connectivity/usb/host
- OpenPGP Card Spec: https://g10code.com/docs/openpgp-card-2.0.pdf

### Related Projects
- Windows Context Menu: `bin/windows_context_menu/`
- macOS Context Menu: `bin/macos_context_menu/`
- Outlook Integration: `outlook_helper/` and `outlook_addin/`

---

## Support

This is a complex project requiring Android development expertise and hardware access for testing.

**For Development Questions:**
- Review IMPLEMENTATION_PLAN.md
- Check Android USB Host API documentation
- Test with real hardware early and often

**For SmartPGP Card Questions:**
- See SmartPGP documentation: https://github.com/ANSSI-FR/SmartPGP
- Review Windows/macOS implementations in this repository

---

## Contributing

To contribute to development:
1. Review IMPLEMENTATION_PLAN.md for architecture
2. Follow Android development best practices
3. Test with real hardware
4. Ensure cross-platform file format compatibility
5. Document all code
6. Write unit tests where possible

---

**Status**: Project initialized, ready for implementation
**Branch**: Androidgpg
**Target**: Full-featured Android app for AEPGP file encryption via USB OTG
