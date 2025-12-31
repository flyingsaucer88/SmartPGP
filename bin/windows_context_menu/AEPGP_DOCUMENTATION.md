# AEPGP Context Menu - Complete Documentation

**Version 1.2.0** | Last Updated: 2025-12-31

---

## 📑 Table of Contents

### Quick Start
1. [Overview](#overview)
2. [Quick Start Guide](#quick-start-guide)
3. [What's New in Version 1.2.0](#whats-new-in-version-120)

### Installation & Setup
4. [System Requirements](#system-requirements)
5. [Installation Methods](#installation-methods)
6. [First-Time Setup](#first-time-setup)
7. [Uninstallation](#uninstallation)

### User Guide
8. [Using AEPGP Context Menu](#using-aepgp-context-menu)
   - [Encrypting Files](#encrypting-files)
   - [Decrypting Files](#decrypting-files)
   - [Generating Keys on Card](#generating-keys-on-card)
   - [Changing Your PIN](#changing-your-pin)
   - [Importing PFX Certificates](#importing-pfx-certificates)

### Troubleshooting
9. [Common Issues & Solutions](#common-issues--solutions)
10. [Debug Logging](#debug-logging)

### Building & Distribution
11. [Building from Source](#building-from-source)
   - [Building Standalone EXE](#building-standalone-exe)
   - [Building MSI Installer](#building-msi-installer)
   - [Adding Custom Icon](#adding-custom-icon)
   - [Updating Version Information](#updating-version-information)
12. [Distribution Guide](#distribution-guide)

### Technical Documentation
13. [Technical Architecture](#technical-architecture)
14. [Security Model](#security-model)
15. [AEPGP-Specific Customizations](#aepgp-specific-customizations)
16. [File Structure](#file-structure)
17. [Registry Entries](#registry-entries)
18. [Encrypted File Format](#encrypted-file-format)

### Development & Testing
19. [Test Suite Documentation](#test-suite-documentation)
   - [GPG Lock Issue Fix](#gpg-lock-issue-fix)
   - [PIN Tracking Fix](#pin-tracking-fix)
20. [Upgrade Notes](#upgrade-notes)

### Reference
21. [Version History](#version-history)
22. [License](#license)
23. [Credits & Support](#credits--support)

---

## Overview

**AEPGP Context Menu** provides seamless Windows Explorer integration for encrypting and decrypting files using your AEPGP smart card with RSA+AES hybrid encryption.

### Key Features

- ✅ **Right-click to Encrypt/Decrypt** - No command line needed
- ✅ **RSA-2048 + AES-256-GCM** - Industry-standard hybrid encryption
- ✅ **Direct APDU Communication** - No GPG keyring required
- ✅ **Automatic Card Detection** - Supports AmbiSecure tokens
- ✅ **PIN Management** - Change your card PIN with automated GPG integration
- ✅ **Key Generation** - Generate RSA-2048 keys directly on your card
- ✅ **Debug Logging** - Comprehensive troubleshooting information
- ✅ **Secure by Design** - Private keys never leave the smart card

---

## Quick Start Guide

### For End Users

**Installation (3 Easy Steps):**

1. **Install Prerequisites**
   - Download GnuPG from [gpg4win.org](https://www.gpg4win.org/)

2. **Run the Installer**
   - Double-click `AEPGP_Context_Menu-1.2.0-win64.msi`
   - Follow the installation wizard

3. **Set Up Your Card (First Time Only)**
   ```cmd
   gpg --card-edit
   > admin
   > generate
   ```

**Usage:**
- **Encrypt:** Right-click file → "Encrypt with AEPGP"
- **Decrypt:** Right-click `.enc` file → "Decrypt with AEPGP"
- **Windows 11:** Click "Show more options" first

---

## What's New in Version 1.2.0

### New Features
- ✨ **Automated PIN Change** - Change your card PIN with automated GPG integration
- ✨ **Hybrid PIN Change Method** - Combines APDU verification with GPG passwd command
- ✨ **Improved Test Suite** - Comprehensive testing with GPG lock handling

### Improvements
- 🔧 **GPG Process Management** - Automatic termination of GPG agent after operations
- 🔧 **PIN Tracking** - Dynamic PIN tracking throughout card lifecycle
- 🔧 **Debug Logging Enhancements** - Better diagnostic information

### Bug Fixes
- 🐛 Fixed GPG smart card lock issue preventing card access
- 🐛 Fixed PIN verification failures after key generation
- 🐛 Fixed PIN change compatibility across OpenPGP cards

---

## System Requirements

### Hardware
- **AmbiSecure AEPGP Token** (ATR: `3B D5 18 FF 81 B1 FE 45 1F C3 80 73 C8 21 10 6F`)
- **USB Smart Card Reader**

### Software
- **Windows 10 or Windows 11**
- **GnuPG** (from [gpg4win.org](https://www.gpg4win.org/))
- Python not required for end users (bundled in installer)

---

## Installation Methods

### Option 1: MSI Installer (Recommended)

**Advantages:**
- ✅ Professional installer wizard
- ✅ Appears in Add/Remove Programs
- ✅ Group Policy deployable
- ✅ Automatic upgrade support
- ✅ Repair functionality

**Steps:**
1. Download `AEPGP_Context_Menu-1.2.0-win64.msi`
2. Double-click the MSI file
3. Follow the installation wizard
4. Context menu items installed automatically

**Silent Installation (IT Departments):**
```cmd
msiexec /i AEPGP_Context_Menu-1.2.0-win64.msi /quiet /norestart
```

### Option 2: Manual Installation (Advanced)

**Prerequisites:**
- Python 3.7 or later
- Required libraries: `pip install pyscard cryptography`

**Steps:**
1. Open `windows_context_menu` folder
2. Right-click `install_menu.py` → "Run as administrator"
3. Or via Command Prompt (as Administrator):
   ```cmd
   python install_menu.py
   ```

---

## First-Time Setup

After installation, initialize your AEPGP card:

### Generate Keys on Card

**Option 1: Context Menu (Recommended)**
1. Insert your AEPGP card
2. Right-click Desktop background
3. Select "AEPGP: Generate Keys in Card"
4. Wait 30-60 seconds for key generation

**Option 2: GPG Command Line**
```cmd
gpg --card-edit
> admin
> generate
> (follow prompts)
> quit
```

### Set Custom PIN

**Default PIN:** `123456`

**To change:**
1. Right-click Desktop background
2. Select "AEPGP: Change Card PIN"
3. Enter current PIN
4. Enter new PIN (twice for confirmation)

**Or via GPG:**
```cmd
gpg --card-edit
> admin
> passwd
> 1 (change PIN)
> (enter current PIN: 123456)
> (enter new PIN)
> quit
```

---

## Using AEPGP Context Menu

### Encrypting Files

1. **Insert your AEPGP card** into the reader
2. **Right-click any file** in Windows Explorer
3. Select **"Encrypt with AEPGP"**
   - Windows 11: Click "Show more options" first
   - Or use SHIFT+Right-click
4. Enter your card PIN when prompted (default: 123456)
5. Encrypted file created with `.enc` extension

**Encryption Details:**
- Algorithm: RSA-2048 + AES-256-GCM hybrid encryption
- RSA encrypts random AES-256 key using card's public key
- AES-256-GCM encrypts file data (fast symmetric encryption)
- File format: `[key_len][encrypted_key][IV][auth_tag][ciphertext]`

### Decrypting Files

1. **Insert your AEPGP card** into the reader
2. **Right-click encrypted file** (`.enc`, `.gpg`, `.pgp`, or `.asc`)
3. Select **"Decrypt with AEPGP"**
4. Enter your card PIN when prompted
5. Decrypted file created (original filename restored)

**Decryption Details:**
- Uses PSO:DECIPHER APDU command to decrypt AES key
- Card's private key decrypts the AES key
- AES-256-GCM decrypts file data
- Private key never leaves the card

### Generating Keys on Card

1. Right-click Desktop background
2. Select "AEPGP: Generate Keys in Card"
3. Confirm key generation
4. Wait 30-60 seconds
5. Success message displayed

**Note:** Generates RSA-2048 key pair directly on the smart card.

### Changing Your PIN

**New in v1.2.0:** Automated PIN change with GPG integration

1. Right-click Desktop background
2. Select "AEPGP: Change Card PIN"
3. Read the information dialog
4. Enter current PIN
5. Enter new PIN (6-127 characters)
6. Confirm new PIN
7. Success message displayed

**Technical Process:**
1. Verifies current PIN via APDU command
2. Disconnects from card
3. Uses automated GPG passwd command
4. Terminates GPG agent
5. Reconnects and verifies new PIN

**PIN Requirements:**
- Minimum: 6 characters
- Maximum: 127 characters
- Recommended: 6-8 digits

### Importing PFX Certificates

1. Right-click `.pfx` or `.p12` file
2. Select "AEPGP: Import to Card"
3. Enter PFX password when prompted

**Note:** This feature is currently in development.

---

## Common Issues & Solutions

### "AEPGP card not found" Error

**Problem:** Context menu handler cannot detect your AEPGP card

**Solutions:**
- ✅ Make sure smart card reader is connected
- ✅ Insert AEPGP card into reader
- ✅ Try removing and re-inserting card
- ✅ Check Device Manager for reader
- ✅ Verify ATR matches: `3B D5 18 FF 81 B1 FE 45 1F C3 80 73 C8 21 10 6F`
- ✅ Check debug log: `%TEMP%\aepgp_debug.log`

### "No keys on card" Error

**Problem:** Card doesn't have encryption keys

**Solutions:**
1. Generate keys: Right-click Desktop → "AEPGP: Generate Keys in Card"
2. Or use GPG: `gpg --card-edit` → `admin` → `generate`

### "Wrong PIN" Error

**Problem:** Incorrect PIN entered

**Solutions:**
- Default PIN is `123456`
- After 3 failed attempts, card locks
- Check retry counter: `gpg --card-status`
- If locked, use Admin PIN (default: `12345678`) to unlock

### "Decryption failed: SW=6F00" Error

**Problem:** File encrypted with incompatible padding or wrong key

**Solutions:**
- Ensure file was encrypted with same card
- Re-encrypt file with updated encryption method
- Verify card has correct encryption key

### Context Menu Items Don't Appear

**Windows 11:**
- Options appear in "Show more options" (legacy menu)
- Or use SHIFT+Right-click for direct access

**Re-run installer:**
- Run as Administrator
- Check for error messages

**Restart Windows Explorer:**
- Task Manager → Windows Explorer → Restart

**Verify registry entries:**
- Open Registry Editor (regedit)
- Check: `HKEY_CLASSES_ROOT\*\shell\AEPGP.Encrypt`
- Check: `HKEY_CLASSES_ROOT\.enc\shell\AEPGP.Decrypt`

### Python Import Errors

**Problem:** "ModuleNotFoundError: No module named 'smartcard'" or 'cryptography'

**Solution:**
```cmd
pip install pyscard cryptography
```

If using multiple Python installations:
```cmd
py -3 -m pip install pyscard cryptography
```

### PIN Change Fails with SW=6982

**Problem:** Security condition not satisfied (wrong PIN)

**Cause:** PIN was reset to factory default after key generation

**Solution:**
- After key generation, default PIN is `123456`
- Use `123456` as current PIN when changing
- The test script tracks this automatically

### Card Access Fails After GPG Operations

**Problem:** "Card not found" after using `gpg --card-edit`

**Cause:** GPG's `scdaemon` holds exclusive lock on card

**Solution:**
```cmd
gpgconf --kill scdaemon
gpgconf --kill gpg-agent
```

**Automatic:** The AEPGP tools now handle this automatically in v1.2.0

---

## Debug Logging

### Log Location

**Windows:** `C:\Users\<YourUsername>\AppData\Local\Temp\aepgp_debug.log`

**Quick Access:**
1. Press `Win + R`
2. Type: `%TEMP%`
3. Press Enter
4. Look for `aepgp_debug.log`

### What Gets Logged

- ✅ Timestamp (millisecond precision)
- ✅ Operation type (Encryption/Decryption/PIN Change)
- ✅ File path and size
- ✅ Python version and platform
- ✅ Smart card readers detected
- ✅ Card ATR (hardware identifier)
- ✅ APDU commands and responses
- ✅ GPG command execution
- ✅ Error messages and stack traces

**Privacy:**
- ❌ NO PIN codes
- ❌ NO file contents
- ❌ NO encryption keys

### Log Management

**Automatic Rotation:**
- Logs automatically rotate at 5MB
- Old log renamed to `aepgp_debug.log.old`

**Manual Cleanup:**
```cmd
del %TEMP%\aepgp_debug.log
```

### Using Logs for Troubleshooting

1. Reproduce the issue
2. Open `%TEMP%\aepgp_debug.log`
3. Scroll to bottom (most recent entries)
4. Look for `[ERROR]` entries
5. Check APDU response codes (SW1 SW2)
6. Review GPG stderr output

**Common Error Codes:**
- `SW=9000` - Success
- `SW=6982` - Security condition not satisfied (wrong PIN)
- `SW=6983` - Authentication method blocked (card locked)
- `SW=63CX` - Wrong PIN, X retries remaining
- `SW=6B00` - Wrong parameters
- `SW=6F00` - Card internal error

---

## Building from Source

### Prerequisites for Building

**Required Software:**
- Windows 10 or 11
- Python 3.7 or later
- pip (Python package manager)

**Required Python Packages:**
```cmd
pip install cx_Freeze pyscard cryptography
```

### Building Standalone EXE

**Method 1: Using Batch File (Easiest)**
```cmd
cd windows_context_menu
build_exe.bat
```

**Method 2: Using Python Script**
```cmd
python build_exe.py
```

**Method 3: Manual PyInstaller**
```cmd
pyinstaller --clean aepgp_installer.spec
```

**Output:** `dist/AEPGP_Installer.exe` (~15-25 MB)

### Building MSI Installer

**Using Batch File:**
```cmd
cd windows_context_menu
python create_msi.py bdist_msi
```

**Output:** `dist/AEPGP_Context_Menu-1.2.0-win64.msi` (~20-35 MB)

**Important:** The MSI build is configured for MSI-ONLY creation. No standalone EXE is created during this process.

### Adding Custom Icon

**Quick Method:**
1. Create or obtain a 256x256 PNG image
2. Convert to `.ico` at https://convertio.co/png-ico/
3. Save as `aepgp_icon.ico`
4. Place in `windows_context_menu/` folder
5. Rebuild: `build_exe.bat`

**Using GIMP:**
1. Download GIMP from https://www.gimp.org/
2. Create 256x256 image
3. File → Export As → `aepgp_icon.ico`
4. Select sizes: 16, 32, 48, 256
5. Place in project folder and rebuild

**Icon Guidelines:**
- Size: 256x256 pixels (source)
- Format: .ico with multiple sizes
- Style: Simple, recognizable at small sizes
- Theme: Security-related (lock, shield, key, card)

### Updating Version Information

**Edit `version_info.txt`:**

For version 1.2.0 → 1.3.0:

```python
# Update these lines:
filevers=(1, 3, 0, 0),  # Changed from (1, 2, 0, 0)
prodvers=(1, 3, 0, 0),  # Changed from (1, 2, 0, 0)

# And these:
StringStruct(u'FileVersion', u'1.3.0.0'),  # Changed from '1.2.0.0'
StringStruct(u'ProductVersion', u'1.3.0.0')  # Changed from '1.2.0.0'
```

**Also update `create_msi.py`:**

```python
APP_VERSION = "1.3.0"  # Changed from "1.2.0"
```

**Then rebuild:**
```cmd
build_exe.bat
python create_msi.py bdist_msi
```

---

## Distribution Guide

### What to Distribute

**Option 1: MSI Only (Recommended for Enterprise)**
```
AEPGP_Context_Menu-1.2.0-win64.msi
```

**Option 2: Complete Package**
```
AEPGP_Package/
├── AEPGP_Context_Menu-1.2.0-win64.msi
├── USER_GUIDE.txt
└── README.txt
```

### Silent Installation (IT Departments)

**Silent Install:**
```cmd
msiexec /i AEPGP_Context_Menu-1.2.0-win64.msi /quiet /norestart
```

**With Logging:**
```cmd
msiexec /i AEPGP_Context_Menu-1.2.0-win64.msi /quiet /norestart /l*v install.log
```

**Silent Uninstall:**
```cmd
msiexec /x AEPGP_Context_Menu-1.2.0-win64.msi /quiet /norestart
```

### Group Policy Deployment

1. Place MSI on network share: `\\server\software\AEPGP_Context_Menu-1.2.0.msi`
2. Open Group Policy Management
3. Create new GPO
4. Edit GPO
5. Navigate: Computer Configuration → Policies → Software Settings → Software Installation
6. Right-click → New → Package
7. Select the MSI file
8. Choose "Assigned"
9. Link GPO to target OU

Computers auto-install on next restart.

### Testing Checklist

Before distribution:
- [ ] Runs without Python installed
- [ ] Icon appears correctly
- [ ] Version info visible (Properties → Details)
- [ ] Install works
- [ ] Encryption works with AmbiSecure token
- [ ] Decryption works
- [ ] PIN change works
- [ ] Only AmbiSecure tokens accepted (ATR check)
- [ ] Uninstall works
- [ ] Windows 10 compatible
- [ ] Windows 11 compatible
- [ ] No antivirus false positives

---

## Technical Architecture

### System Components

**1. Registry-Based Integration**
- Creates Windows Registry entries in `HKEY_CLASSES_ROOT`
- Adds context menu items to Windows Explorer
- Executes Python handlers when menu items clicked

**2. Handler Scripts**
- `encrypt_handler.py` - RSA+AES encryption
- `decrypt_handler.py` - Card-based decryption
- `generate_keys_handler.py` - Key generation on card
- `change_pin_handler.py` - PIN change with GPG integration (NEW in v1.2.0)
- `import_pfx_handler.py` - PFX import (planned)

**3. Direct APDU Communication**
- Uses `pyscard` library for smart card communication
- Sends APDU commands directly to AEPGP card
- No GPG keyring required for encryption/decryption

**4. RSA+AES Hybrid Encryption**
- Reads RSA public key from card via APDU
- Generates random AES-256 key and IV
- Encrypts file data with AES-256-GCM (fast)
- Encrypts AES key with RSA-PKCS1v15 using card's public key

### APDU Commands Used

| Command | Description |
|---------|-------------|
| `00 A4 04 00 06 D2 76 00 01 24 01` | SELECT OpenPGP applet |
| `00 47 81 00 02 B8 00` | GET PUBLIC KEY (decryption key) |
| `00 20 00 82 [Lc] [PIN]` | VERIFY PIN |
| `00 2A 80 86 [data]` | PSO:DECIPHER (decrypt) |
| `00 24 00 82 [Lc] [old_PIN][new_PIN]` | CHANGE REFERENCE DATA (not used in v1.2.0) |

### Cryptographic Algorithms

- **RSA:** 2048-bit keys with PKCS#1 v1.5 padding
- **AES:** 256-bit keys with GCM mode (12-byte IV, 16-byte auth tag)
- **Key Exchange:** RSA encrypts random AES key
- **Data Encryption:** AES-256-GCM for file content

---

## Security Model

### Key Security Features

**1. Private Keys Never Leave Card**
- All private key operations performed on smart card
- Decryption happens on-card via PSO:DECIPHER
- No key export possible

**2. PIN Protection**
- PIN required for decryption operations
- PIN never stored by application
- Card locks after 3 failed attempts

**3. Hybrid Encryption**
- RSA provides secure key exchange
- AES provides fast data encryption
- GCM mode provides authenticated encryption

**4. AEPGP Card Detection**
- Only accepts AmbiSecure tokens with specific ATR
- Rejects other OpenPGP cards
- Hardware-level authentication

### Encrypted File Format

```
[4 bytes: encrypted AES key length (big-endian)]
[256 bytes: RSA-encrypted AES-256 key]
[12 bytes: IV for AES-GCM]
[16 bytes: GCM authentication tag]
[remaining: AES-256-GCM encrypted file data]
```

### Security Considerations

- ✅ No GPG keyring dependency
- ✅ No PIN storage in application
- ✅ Card communication over PC/SC
- ✅ Private keys remain on smart card
- ✅ Authenticated encryption (GCM)
- ⚠️ Debug logs may contain file paths (no keys/PINs)
- ⚠️ PIN entered via tkinter dialog (consider pinentry for production)

---

## AEPGP-Specific Customizations

### 1. AmbiSecure Token Detection

**Restricted to specific ATR:**
```
3B D5 18 FF 81 B1 FE 45 1F C3 80 73 C8 21 10 6F
```

**Implementation:** `card_utils.py`
- Added `AMBISECURE_ATR` constant
- Added `verify_ambisecure_atr()` function
- Modified `find_aepgp_card()` to verify ATR
- Only AmbiSecure tokens accepted

### 2. AEPGP Branding

**All user-facing text uses "AEPGP":**
- Context menu items
- Dialog titles and messages
- Error messages
- Documentation

**Files Updated:**
- `card_utils.py` - Renamed classes and functions
- `encrypt_handler.py` - Updated messages
- `decrypt_handler.py` - Updated messages
- `change_pin_handler.py` - Updated messages
- `install_menu.py` - Registry keys use AEPGP
- `uninstall_menu.py` - AEPGP registry keys

### 3. PIN Management (v1.2.0)

**Hybrid PIN Change Method:**
1. Verify current PIN via APDU command
2. Disconnect from card
3. Use automated GPG passwd command
4. Terminate GPG agent
5. Reconnect and verify new PIN

**Benefits:**
- ✅ More reliable than pure APDU method
- ✅ Works across all OpenPGP cards
- ✅ Fully automated (no manual GPG steps)
- ✅ Proper cleanup of GPG processes

---

## File Structure

```
windows_context_menu/
├── handlers/
│   ├── card_utils.py              # Smart card detection (AEPGP ATR)
│   ├── card_key_reader.py         # Read public key via APDU
│   ├── encrypt_handler.py         # RSA+AES encryption
│   ├── decrypt_handler.py         # Card-based decryption
│   ├── generate_keys_handler.py   # Generate keys on card
│   ├── change_pin_handler.py      # PIN change with GPG (NEW v1.2.0)
│   ├── import_pfx_handler.py      # Import PFX (planned)
│   ├── rsa_crypto.py              # RSA+AES encryption logic
│   ├── rsa_decrypt.py             # RSA+AES decryption logic
│   ├── debug_logger.py            # Debug logging module
│   └── __init__.py
├── dist/
│   └── AEPGP_Context_Menu-1.2.0-win64.msi  # MSI installer
├── install_menu.py                # Installer script
├── uninstall_menu.py              # Uninstaller script
├── create_msi.py                  # MSI builder (v1.2.0)
├── requirements.txt               # Python dependencies
├── test_all_features.py           # Comprehensive test suite
└── AEPGP_DOCUMENTATION.md         # This file
```

---

## Registry Entries

### For Encryption (all files)
```
HKEY_CLASSES_ROOT\*\shell\AEPGP.Encrypt
    (Default) = "Encrypt with AEPGP"
    \command
        (Default) = "C:\...\pythonw.exe" "C:\...\encrypt_handler.py" "%1"
```

### For Decryption (.enc, .gpg, .pgp, .asc files)
```
HKEY_CLASSES_ROOT\.enc\shell\AEPGP.Decrypt
    (Default) = "Decrypt with AEPGP"
    \command
        (Default) = "C:\...\pythonw.exe" "C:\...\decrypt_handler.py" "%1"
```

### For Generate Keys (Desktop background)
```
HKEY_CLASSES_ROOT\Directory\Background\shell\AEPGP.GenerateKeys
    (Default) = "AEPGP: Generate Keys in Card"
    \command
        (Default) = "C:\...\pythonw.exe" "C:\...\generate_keys_handler.py"
```

### For Change PIN (Desktop background) - NEW v1.2.0
```
HKEY_CLASSES_ROOT\Directory\Background\shell\AEPGP.ChangePIN
    (Default) = "AEPGP: Change Card PIN"
    \command
        (Default) = "C:\...\pythonw.exe" "C:\...\change_pin_handler.py"
```

### For Import PFX (.pfx, .p12 files)
```
HKEY_CLASSES_ROOT\.pfx\shell\AEPGP.ImportPFX
    (Default) = "AEPGP: Import to Card"
    \command
        (Default) = "C:\...\pythonw.exe" "C:\...\import_pfx_handler.py" "%1"
```

---

## Encrypted File Format

### File Structure

```
[Offset 0-3]     4 bytes:  Encrypted AES key length (big-endian uint32)
[Offset 4-259]   256 bytes: RSA-encrypted AES-256 key (PKCS#1 v1.5)
[Offset 260-271] 12 bytes:  AES-GCM IV (random)
[Offset 272-287] 16 bytes:  GCM authentication tag
[Offset 288+]    Variable:  AES-256-GCM encrypted file data
```

### Example

For a 1KB file:
```
Total encrypted size = 4 + 256 + 12 + 16 + 1024 = 1312 bytes
```

### Decryption Process

1. Read first 4 bytes → encrypted key length
2. Read next 256 bytes → RSA-encrypted AES key
3. Send encrypted AES key to card via PSO:DECIPHER
4. Card decrypts and returns AES key
5. Read IV (12 bytes) and auth tag (16 bytes)
6. Decrypt file data with AES-256-GCM using key, IV, and tag
7. Verify authentication tag
8. Write decrypted data to output file

---

## Test Suite Documentation

### Overview

**File:** `test_all_features.py`

**Purpose:** Comprehensive testing of all AEPGP features

**Tests:**
1. Card Detection
2. Delete Keys (factory reset)
3. Generate RSA-2048 Keys
4. Change PIN
5. Encryption
6. Decryption
7. PFX Import (placeholder)

### GPG Lock Issue Fix

**Problem:** GPG's `scdaemon` holds exclusive lock on smart card

**Root Cause:**
- `scdaemon` runs as background process
- Maintains exclusive PC/SC access
- Doesn't terminate automatically
- Blocks pyscard access

**Solution:** `kill_gpg_agent()` function

```python
def kill_gpg_agent():
    """Kill GPG agent and scdaemon to release card lock."""
    subprocess.run("gpgconf --kill scdaemon", ...)
    subprocess.run("gpgconf --kill gpg-agent", ...)
    time.sleep(1)
```

**Integration:**
- Called after `gpg --card-edit` operations
- Called in `wait_for_card_reconnect()`
- Ensures card accessibility for subsequent tests

### PIN Tracking Fix

**Problem:** PIN resets to factory default after key generation

**Root Cause:**
- OpenPGP cards reset user PIN to `123456` after `gpg generate`
- Test script was using custom default `190482`
- Resulted in SW=6982 errors (wrong PIN)

**Solution:** Dynamic PIN tracking

```python
FACTORY_DEFAULT_PIN = "123456"  # OpenPGP factory default
CUSTOM_DEFAULT_PIN = "190482"   # Custom default
current_pin = CUSTOM_DEFAULT_PIN  # Tracks active PIN
```

**Implementation:**
- `test_generate_keys()` sets `current_pin = FACTORY_DEFAULT_PIN`
- `test_change_pin()` updates `current_pin` after successful change
- `test_decryption()` uses `current_pin` for verification

### Test Results

**Version 1.2.0:** All 7 tests pass
- ✅ Test 1: Card Detection
- ✅ Test 2: Delete Keys
- ✅ Test 3: Generate Keys
- ✅ Test 4: Change PIN (automated GPG method)
- ✅ Test 5: Encryption
- ✅ Test 6: Decryption
- ✅ Test 7: PFX Import (placeholder)

---

## Upgrade Notes

### Automatic Upgrade Feature

**Upgrade Code:** `{A1B2C3D4-E5F6-4A5B-8C9D-0E1F2A3B4C5D}`

**This code:**
- ⚠️ NEVER CHANGES across all versions
- Allows Windows Installer to detect previous installations
- Triggers automatic uninstallation of older versions

### Installation Behavior

**Installing v1.2.0 over v1.1.0:**
1. Windows Installer detects upgrade code match
2. Automatically uninstalls v1.1.0
3. Installs v1.2.0
4. No user action required

### Version Upgrade Guidelines

- **Major version (x.0.0):** Breaking changes, major features
- **Minor version (1.x.0):** New features, enhancements
- **Patch version (1.0.x):** Bug fixes, minor improvements

### Testing Upgrades

1. Install old version
2. Run new MSI installer
3. Verify automatic uninstall
4. Verify new version installs
5. Test context menu functionality
6. Check Add/Remove Programs (no duplicates)

---

## Version History

### Version 1.2.0 (2025-12-31)
- ✨ **NEW:** Automated PIN change functionality with GPG integration
- ✨ **NEW:** Hybrid PIN change method (APDU verification + GPG passwd)
- 🔧 **IMPROVED:** Automatic GPG process management (kill scdaemon/gpg-agent)
- 🔧 **IMPROVED:** Dynamic PIN tracking in test suite
- 🐛 **FIXED:** GPG smart card lock issue preventing card access
- 🐛 **FIXED:** PIN verification failures after key generation
- 🐛 **FIXED:** PIN change compatibility across OpenPGP cards
- 📝 **DOCUMENTATION:** Comprehensive combined documentation with index
- 📝 **DOCUMENTATION:** Test fix summaries (GPG lock, PIN tracking)

### Version 1.1.0
- **NEW:** RSA+AES hybrid encryption (no GPG keyring required)
- **NEW:** Direct APDU communication with AEPGP card
- **NEW:** Generate keys on card via context menu
- **NEW:** Import PFX to card (planned feature)
- **NEW:** Debug logging to %TEMP%\aepgp_debug.log
- **IMPROVED:** Decrypt restores original file extensions
- **IMPROVED:** Logs added to top of debug file
- **CHANGED:** .enc file extension instead of .gpg
- **CHANGED:** No dependency on GPG keyring
- **FIXED:** Gemalto card detection for NXP JCOP cards

### Version 1.0.1
- MSI installer support
- Automatic upgrade functionality
- Bug fixes

### Version 1.0.0
- Initial release
- Basic GPG-based encryption/decryption
- AmbiSecure token detection
- AEPGP branding
- Context menu integration

---

## Uninstallation

### Option 1: MSI Uninstall (Recommended)

**Via Windows Settings:**
1. Windows Settings → Apps
2. Find "AEPGP Context Menu"
3. Click "Uninstall"
4. Confirm uninstallation

**Via Control Panel:**
1. Control Panel → Programs → Programs and Features
2. Find "AEPGP Context Menu"
3. Right-click → Uninstall

**Silent Uninstall:**
```cmd
msiexec /x AEPGP_Context_Menu-1.2.0-win64.msi /quiet /norestart
```

### Option 2: Manual Uninstall

1. Open `windows_context_menu` folder
2. Right-click `uninstall_menu.py` → "Run as administrator"
3. Or via Command Prompt (as Administrator):
   ```cmd
   python uninstall_menu.py
   ```
4. Confirm when prompted
5. Wait for completion

**What Gets Removed:**
- Registry entries in HKEY_CLASSES_ROOT
- Context menu items
- Installed files (if using MSI)

---

## License

Based on **SmartPGP** project by ANSSI (French National Cybersecurity Agency)

**License:** GNU General Public License v2 (GPL v2)

**Customizations:** AEPGP-specific modifications for AmbiSecure token support

**Original Project:** https://github.com/ANSSI-FR/SmartPGP

---

## Credits & Support

### Credits

- **SmartPGP JavaCard Implementation:** ANSSI (French National Cybersecurity Agency)
- **Context Menu Integration:** Developed for AEPGP users on Windows
- **Encryption:** Python cryptography library
- **Smart Card Communication:** pyscard library

### Support

**For AEPGP Context Menu Issues:**
- Check debug log: `%TEMP%\aepgp_debug.log`
- Review this documentation
- Contact your AEPGP administrator

**For SmartPGP Card Issues:**
- See SmartPGP documentation
- Visit: https://github.com/ANSSI-FR/SmartPGP

**For pyscard Issues:**
- Visit: https://pyscard.sourceforge.io/

**For cryptography Library Issues:**
- Visit: https://cryptography.io/

### Reporting Issues

When reporting issues, include:
- Windows version (10 or 11)
- AEPGP Context Menu version
- Card ATR (from debug log)
- Error messages (exact text)
- Relevant debug log entries
- Steps to reproduce

---

**End of Documentation**

*AEPGP Context Menu v1.2.0 - Professional Windows Integration for AEPGP Smart Cards*
