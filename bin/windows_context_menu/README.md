# AEPGP Windows Context Menu

**Version 1.3.1** | Professional Windows Integration for AEPGP Smart Cards

---

## Table of Contents

### Quick Start
- [Overview](#overview)
- [Quick Start Guide](#quick-start-guide)
- [System Requirements](#system-requirements)

### Installation & Setup
- [Installation](#installation)
- [First-Time Setup](#first-time-setup)
- [Uninstallation](#uninstallation)

### User Guide
- [Using AEPGP Context Menu](#using-aepgp-context-menu)
  - [Encrypting Files](#encrypting-files)
  - [Decrypting Files](#decrypting-files)
  - [Generating Keys on Card](#generating-keys-on-card)
  - [Changing Your PIN](#changing-your-pin)

### Troubleshooting
- [Common Issues & Solutions](#common-issues--solutions)
- [Debug Logging](#debug-logging)

### Technical Documentation
- [Technical Architecture](#technical-architecture)
- [Security Model](#security-model)
- [APDU Commands Reference](#apdu-commands-reference)
- [Implemented Features (v1.3.2)](#implemented-features-v132)
  - [Enhanced File Visibility Management](#enhanced-file-visibility-management-)
  - [Key Alias Management](#key-alias-management-)
- [File Structure](#file-structure)
- [Encrypted File Format](#encrypted-file-format)

### Development
- [Building from Source](#building-from-source)
- [Testing Recent Changes](#testing-recent-changes)
- [Version History](#version-history)
- [License](#license)

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

### Installation (3 Easy Steps)

1. **Install Prerequisites**
   - Download GnuPG from [gpg4win.org](https://www.gpg4win.org/)

2. **Run the Installer**
   - Double-click `AEPGP_Context_Menu-1.3.1-win64.msi`
   - Follow the installation wizard

3. **Set Up Your Card (First Time Only)**
   - Insert AEPGP card
   - Right-click Desktop → "AEPGP: Generate Keys in Card"
   - Wait 30-60 seconds

### Basic Usage

- **Encrypt:** Right-click file → "Encrypt with AEPGP"
- **Decrypt:** Right-click `.enc` file → "Decrypt with AEPGP"
- **Windows 11:** Click "Show more options" first

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

## Installation

### Option 1: MSI Installer (Recommended)

**Advantages:**
- ✅ Professional installer wizard
- ✅ Appears in Add/Remove Programs
- ✅ Group Policy deployable
- ✅ Automatic upgrade support
- ✅ Repair functionality

**Steps:**
1. Download `AEPGP_Context_Menu-1.3.1-win64.msi`
2. Double-click the MSI file
3. Follow the installation wizard
4. Context menu items installed automatically

**Silent Installation (IT Departments):**
```cmd
msiexec /i AEPGP_Context_Menu-1.3.1-win64.msi /quiet /norestart
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

### Change Default PIN

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
3. If keys already exist, you'll see the current alias and be asked to confirm overwrite
4. Enter a key alias (human-readable name for the key pair)
5. Confirm with Admin PIN (default: `12345678`)
6. Wait 30-60 seconds for key generation
7. Success message displayed with your alias

**Key Alias Feature:**
- The alias is stored directly on the card (Private DO 0x0102)
- Can be read anytime without PIN authentication
- Helps identify which card/key pair you're using
- Persists across card removal and reinsertion
- Maximum 255 ASCII characters

**Note:** Generates RSA-2048 key pair directly on the smart card using direct APDU commands.

### Changing Your PIN

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

### Automatic File Visibility Management

**NEW in v1.3.2:** Encrypted files (.enc) are automatically hidden when no AEPGP card is present and shown when a card is inserted.

**How It Works:**
- A background watcher service runs at user logon
- Checks for card presence every 5 seconds (configurable)
- Rescans folders every 60 seconds for new .enc files (configurable)
- Automatically sets Windows hidden attribute on .enc files

**Monitored Folders (default):**
- Desktop
- Documents
- Downloads

**Configuration:**

Set environment variables to customize behavior:

```cmd
REM Custom watch paths (semicolon-separated)
setx AEPGP_WATCH_PATHS "C:\MyFiles;D:\SecureData"

REM Card detection interval in seconds (default: 5)
setx AEPGP_POLL_INTERVAL_SEC "10"

REM Full file rescan interval in seconds (default: 60)
setx AEPGP_RESCAN_INTERVAL_SEC "120"
```

**Viewing Hidden Files:**
- Insert your AEPGP card (files become visible automatically)
- Or enable "Show hidden files" in Windows Explorer

**Skipped Directories:**
The watcher automatically skips: `.git`, `node_modules`, `__pycache__`, `AppData`

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

### Card Access Fails After GPG Operations

**Problem:** "Card not found" after using `gpg --card-edit`

**Cause:** GPG's `scdaemon` holds exclusive lock on card

**Solution:**
```cmd
gpgconf --kill scdaemon
gpgconf --kill gpg-agent
```

**Note:** The AEPGP tools handle this automatically in v1.2.0+

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

### Common Error Codes

- `SW=9000` - Success
- `SW=6982` - Security condition not satisfied (wrong PIN)
- `SW=6983` - Authentication method blocked (card locked)
- `SW=63CX` - Wrong PIN, X retries remaining
- `SW=6A88` - Referenced data not found (no keys on card)
- `SW=6B00` - Wrong parameters
- `SW=6F00` - Card internal error

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
- `generate_keys_handler.py` - Key generation on card (uses direct APDU)
- `change_pin_handler.py` - PIN change with GPG integration
- `import_pfx_handler.py` - PFX import (disabled - see technical notes)

**3. Direct APDU Communication**
- Uses `pyscard` library for smart card communication
- Sends APDU commands directly to AEPGP card
- No GPG keyring required for encryption/decryption

**4. RSA+AES Hybrid Encryption**
- Reads RSA public key from card via APDU
- Generates random AES-256 key and IV
- Encrypts file data with AES-256-GCM (fast)
- Encrypts AES key with RSA-PKCS1v15 using card's public key

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

---

## APDU Commands Reference

### Core Commands

| Command | Description | APDU |
|---------|-------------|------|
| SELECT OpenPGP | Select OpenPGP applet | `00 A4 04 00 06 D2 76 00 01 24 01` |
| GET PUBLIC KEY | Read decryption public key | `00 47 81 00 02 B8 00` |
| VERIFY PIN | Verify user PIN | `00 20 00 82 [Lc] [PIN]` |
| PSO:DECIPHER | Decrypt data | `00 2A 80 86 [data]` |
| VERIFY ADMIN PIN | Verify admin PIN | `00 20 00 83 [Lc] [PIN]` |
| GENERATE KEY | Generate RSA-2048 key pair | `00 47 80 00 02 B8 00 00` |

### Key Generation Details

**APDU Structure:**
- CLA: `00` (standard)
- INS: `47` (GENERATE ASYMMETRIC KEY PAIR)
- P1: `80` (generate both private and public key)
- P2: `00`
- Lc: `02` (data length)
- Data: `B8 00`
  - `B8` = Decryption/Encryption key slot
  - `00` = Empty template (use card defaults)
- Le: `00` (expect response)

**Response:**
- Public key data in TLV format (7F 49 ...)
- Length: 270 bytes for RSA-2048
- SW=61XX if more data available (need GET RESPONSE)
- SW=9000 on complete success

### Buffer Limitations

**SmartPGP Internal Buffer:** 1280 bytes (0x500)
- Location: `SmartPGP/src/fr/anssi/smartpgp/Constants.java:29`
- This limitation affects PFX import functionality
- Command chaining fails when importing RSA-2048 keys (~1843 bytes required)
- See technical notes for details

---

## Implemented Features (v1.3.2)

### Enhanced File Visibility Management ✅

Automatically hide .enc files when AEPGP card is not present and show them when card is inserted.

**Implemented Features:**
- ✅ Background visibility watcher service
- ✅ Runs automatically at user logon via Windows startup registry
- ✅ Configurable watch paths via `AEPGP_WATCH_PATHS` environment variable
- ✅ Configurable polling intervals (`AEPGP_POLL_INTERVAL_SEC`, `AEPGP_RESCAN_INTERVAL_SEC`)
- ✅ Automatically skips system directories (`.git`, `node_modules`, `__pycache__`, `AppData`)
- ✅ Minimal CPU and memory footprint
- ✅ Card presence detection every 5 seconds (default)
- ✅ Full file rescan every 60 seconds (default)

**How to Configure:**
```cmd
REM Set custom watch paths (semicolon-separated)
setx AEPGP_WATCH_PATHS "C:\MyFiles;D:\SecureData"

REM Set card detection interval (default: 5 seconds)
setx AEPGP_POLL_INTERVAL_SEC "10"

REM Set file rescan interval (default: 60 seconds)
setx AEPGP_RESCAN_INTERVAL_SEC "120"
```

**Default Monitored Folders:**
- `%USERPROFILE%\Desktop`
- `%USERPROFILE%\Documents`
- `%USERPROFILE%\Downloads`

**Implementation Details:**
- Uses Windows hidden file attribute (not encryption)
- Background process runs as `pythonw.exe` (no console window)
- Logs to `%TEMP%\aepgp_debug.log`
- Installed automatically during setup
- Removed automatically during uninstall

---

### Key Alias Management ✅

Store human-readable names for key pairs directly on the AEPGP card.

**Implemented Features:**
- ✅ Store alias in Private DO 0x0102 on card
- ✅ Read alias without PIN authentication
- ✅ Prompt for alias during key generation
- ✅ Show existing alias when overwriting keys
- ✅ Maximum 255 ASCII characters
- ✅ Persists across card removal and reinsertion
- ✅ No external storage required (alias lives on card)

**Use Cases:**
- Identify which card you're using (e.g., "Work Card", "Personal Card")
- Track key pair ownership across multiple cards
- Quick identification without PIN entry

**APDU Commands Used:**
- `00 CA 01 02 00` - GET DATA (read alias)
- `00 DA 01 02 [Lc] [alias]` - PUT DATA (write alias)

**Technical Details:**
- Uses SmartPGP Private Data Object (DO) 0x0102
- Supported by SmartPGP applet (see `SmartPGPApplet.java` lines 1019-1050)
- No PIN required for reading
- Admin PIN required for writing (during key generation)

---

## File Structure

```
windows_context_menu/
├── handlers/
│   ├── card_utils.py              # Smart card detection (AEPGP ATR)
│   ├── card_key_reader.py         # Read public key via APDU
│   ├── encrypt_handler.py         # RSA+AES encryption
│   ├── decrypt_handler.py         # Card-based decryption
│   ├── generate_keys_handler.py   # Generate keys on card (direct APDU)
│   ├── change_pin_handler.py      # PIN change with GPG
│   ├── import_pfx_handler.py      # Import PFX (disabled)
│   ├── rsa_crypto.py              # RSA+AES encryption logic
│   ├── rsa_decrypt.py             # RSA+AES decryption logic
│   ├── debug_logger.py            # Debug logging module
│   └── __init__.py
├── dist/
│   └── AEPGP_Context_Menu-1.3.2-win64.msi  # MSI installer
├── install_menu.py                # Installer script
├── uninstall_menu.py              # Uninstaller script
├── visibility_watcher.py          # Background file visibility service (NEW v1.3.2)
├── create_msi.py                  # MSI builder
├── requirements.txt               # Python dependencies
├── VERSION                        # Version tracking
├── TODO.md                        # Enhancement roadmap
└── README.md                      # This file
```

---

## Building from Source

### Prerequisites

**Required Software:**
- Windows 10 or 11
- Python 3.7 or later
- pip (Python package manager)

**Required Python Packages:**
```cmd
pip install cx_Freeze pyscard cryptography
```

### Building Standalone EXE

```cmd
cd windows_context_menu
build_exe.bat
```

**Output:** `dist/AEPGP_Installer.exe` (~15-25 MB)

### Building MSI Installer

```cmd
cd windows_context_menu
python create_msi.py bdist_msi
```

**Output:** `dist/AEPGP_Context_Menu-1.3.1-win64.msi` (~20-35 MB)

---

## Testing Recent Changes

This section provides comprehensive testing procedures for the recent fixes and improvements made on January 1-8, 2026.

### Testing v1.3.1 - Key Generation Fix

The v1.3.1 release fixed a critical bug where key generation appeared to succeed but didn't actually create keys on the card. Test the fix with these steps:

#### Prerequisites
- AEPGP card inserted in reader
- AEPGP Context Menu installed (v1.3.1)
- Card should have no keys (factory state) or you can delete existing keys

#### Test 1: Verify Key Generation Works

1. **Delete existing keys (if any):**
   ```cmd
   gpg --card-edit
   > admin
   > factory-reset
   > y
   > yes
   > quit
   ```

2. **Generate keys via Context Menu:**
   - Right-click on Desktop background
   - Select "AEPGP: Generate Keys in Card"
   - Enter Admin PIN when prompted (default: `12345678`)
   - Wait 30-60 seconds
   - Verify success message appears

3. **Verify keys were actually created:**
   ```cmd
   gpg --card-status
   ```

   **Expected Output:** Look for key information section showing generated keys:
   ```
   Signature key ....: [key fingerprint]
   Encryption key....: [key fingerprint]
   Authentication key: [key fingerprint]
   General key info..: [not set]
   ```

4. **Check debug log:**
   - Open: `%TEMP%\aepgp_debug.log`
   - Search for: "Key generation complete"
   - Verify no errors like `SW=6A88` (referenced data not found)

#### Test 2: Verify Encryption Works After Key Generation

1. **Create a test file:**
   ```cmd
   echo "Test encryption content" > C:\temp\test.txt
   ```

2. **Encrypt the file:**
   - Right-click `C:\temp\test.txt`
   - Select "Encrypt with AEPGP"
   - Enter PIN (default: `123456`)
   - Verify `test.txt.enc` is created

3. **Check the encrypted file:**
   ```cmd
   dir C:\temp\test.txt.enc
   ```

   **Expected:** File should exist and be larger than original

4. **Decrypt the file:**
   - Delete or rename `test.txt`
   - Right-click `test.txt.enc`
   - Select "Decrypt with AEPGP"
   - Enter PIN
   - Verify `test.txt` is restored with original content

5. **Verify decrypted content:**
   ```cmd
   type C:\temp\test.txt
   ```

   **Expected Output:** `Test encryption content`

#### Test 3: Verify Direct APDU Communication

1. **Check debug log for APDU commands:**
   - Open: `%TEMP%\aepgp_debug.log`
   - Search for recent key generation operation

   **Expected Log Entries:**
   ```
   [INFO] Verifying Admin PIN via APDU...
   [DEBUG] APDU Command: 00 20 00 83 ...
   [DEBUG] Response: 90 00
   [INFO] Sending GENERATE KEY command via APDU...
   [DEBUG] APDU Command: 00 47 80 00 02 B8 00 00
   [DEBUG] Response: 61 XX (more data available)
   [DEBUG] GET RESPONSE command: 00 C0 00 00 XX
   [DEBUG] Public key data received: 7F 49 ...
   [INFO] Key generation complete: SW=9000
   ```

2. **Verify NO subprocess calls:**
   - Search log for: `python -m smartpgp`
   - **Expected:** Should NOT find any such entries (old broken method)

#### Test 4: Test Error Handling

1. **Test without card inserted:**
   - Remove AEPGP card
   - Right-click Desktop → "AEPGP: Generate Keys in Card"
   - **Expected:** Clear error message: "AEPGP card not found"

2. **Test with wrong Admin PIN:**
   - Insert card
   - Right-click Desktop → "AEPGP: Generate Keys in Card"
   - Enter wrong Admin PIN (e.g., `00000000`)
   - **Expected:** Error message: "Admin PIN verification failed"

3. **Test encryption without keys:**
   - Factory-reset card (see Test 1, step 1)
   - Try to encrypt a file
   - **Expected:** Error message: "No key found in slot" with suggestion to generate keys

### Testing v1.3.2 - File Visibility & Key Alias Features

Test the automatic file visibility management and key alias functionality.

#### Test 8: Key Alias Storage and Retrieval

1. **Generate keys with alias:**
   - Factory reset card (if needed)
   - Right-click Desktop → "AEPGP: Generate Keys in Card"
   - Enter alias: `John Doe Work Key`
   - Enter Admin PIN: `12345678`
   - **Expected:** Success message showing your alias

2. **Verify alias persists:**
   - Remove card from reader
   - Reinsert card
   - Generate keys again (to check existing key detection)
   - **Expected:** Dialog shows "Existing alias: John Doe Work Key"

3. **Verify alias is readable without PIN:**
   - Check debug log: `%TEMP%\aepgp_debug.log`
   - Search for: "GET DATA 0102"
   - **Expected:** Alias read successfully without PIN verification command

#### Test 9: Automatic File Visibility

1. **Setup test environment:**
   - Create a test .enc file on Desktop: `echo test > Desktop\test.txt.enc`
   - Ensure AEPGP card is inserted
   - **Expected:** File should be visible

2. **Test hiding when card removed:**
   - Remove AEPGP card from reader
   - Wait 10 seconds (for watcher to detect)
   - **Expected:** `test.txt.enc` disappears (hidden attribute set)

3. **Test showing when card inserted:**
   - Reinsert AEPGP card
   - Wait 10 seconds (for watcher to detect)
   - **Expected:** `test.txt.enc` reappears (hidden attribute cleared)

4. **Verify watcher is running:**
   ```cmd
   tasklist | findstr pythonw
   ```
   **Expected:** Should find `pythonw.exe` running `visibility_watcher.py`

5. **Check watcher logs:**
   - Open: `%TEMP%\aepgp_debug.log`
   - Search for: "Visibility sync complete"
   - **Expected:** Regular log entries every 60 seconds

#### Test 10: Configuration Customization

1. **Set custom watch paths:**
   ```cmd
   mkdir C:\TestSecure
   echo test > C:\TestSecure\secret.txt.enc
   setx AEPGP_WATCH_PATHS "C:\TestSecure"
   ```

2. **Restart watcher:**
   - Kill existing watcher: `taskkill /IM pythonw.exe /F`
   - Start watcher manually or log off and back on
   - Remove AEPGP card
   - Wait 10 seconds
   - **Expected:** `C:\TestSecure\secret.txt.enc` becomes hidden

3. **Verify custom intervals:**
   ```cmd
   setx AEPGP_POLL_INTERVAL_SEC "3"
   setx AEPGP_RESCAN_INTERVAL_SEC "30"
   ```
   - Restart watcher
   - Check debug log for: "Intervals: poll=3s rescan=30s"

### Testing v1.3.0 - PFX Import Disabled

Verify that PFX import is properly disabled and shows appropriate messaging.

#### Test 5: Verify PFX Import Disabled

1. **Check context menu for .pfx files:**
   - Create or locate a .pfx file
   - Right-click the .pfx file
   - **Expected:** Should NOT see "AEPGP: Import to Card" option

2. **Verify registry entries:**
   ```cmd
   reg query "HKEY_CLASSES_ROOT\.pfx\shell" /s
   ```

   **Expected:** Should NOT find AEPGP.ImportPFX entries

3. **Check installer:**
   - Run MSI installer in repair mode
   - Verify no PFX import option added

### Testing v1.2.0 - PIN Change Functionality

Test the automated PIN change feature with GPG integration.

#### Test 6: PIN Change End-to-End

1. **Change PIN via Context Menu:**
   - Ensure card has default PIN (`123456`)
   - Right-click Desktop → "AEPGP: Change Card PIN"
   - Read information dialog, click OK
   - Enter current PIN: `123456`
   - Enter new PIN: `190482` (or your choice)
   - Confirm new PIN: `190482`
   - **Expected:** Success message

2. **Verify new PIN works:**
   - Try to encrypt a file
   - Enter new PIN (`190482`)
   - **Expected:** Encryption succeeds

3. **Verify old PIN doesn't work:**
   - Try to encrypt another file
   - Enter old PIN (`123456`)
   - **Expected:** "Wrong PIN" error

4. **Check GPG process cleanup:**
   ```cmd
   tasklist | findstr gpg
   ```

   **Expected:** Should NOT find `scdaemon.exe` or `gpg-agent.exe` running after PIN change

5. **Verify debug log:**
   - Open: `%TEMP%\aepgp_debug.log`
   - Search for PIN change operation

   **Expected Log Entries:**
   ```
   [INFO] Verifying current PIN via APDU...
   [DEBUG] APDU Response: 90 00
   [INFO] Disconnecting from card...
   [INFO] Using GPG passwd command...
   [DEBUG] GPG command: gpg --batch --command-fd 0 --status-fd 2 --card-edit
   [INFO] Killing GPG processes...
   [DEBUG] Executed: gpgconf --kill scdaemon
   [DEBUG] Executed: gpgconf --kill gpg-agent
   [INFO] Reconnecting to card...
   [INFO] Verifying new PIN...
   [DEBUG] APDU Response: 90 00
   [INFO] PIN changed successfully
   ```

#### Test 7: PIN Tracking After Key Generation

1. **Factory reset card:**
   ```cmd
   gpg --card-edit
   > admin
   > factory-reset
   ```

2. **Set custom PIN:**
   - Right-click Desktop → "AEPGP: Change Card PIN"
   - Change from `123456` to `190482`

3. **Generate keys:**
   - Right-click Desktop → "AEPGP: Generate Keys in Card"
   - **Note:** Key generation resets PIN to factory default

4. **Test encryption with factory PIN:**
   - Try to encrypt with new PIN (`190482`)
   - **Expected:** Fails
   - Try to encrypt with factory PIN (`123456`)
   - **Expected:** Succeeds (PIN was reset by key generation)

### Test Results Checklist

Use this checklist to track your testing progress:

**v1.3.2 - File Visibility & Key Alias:**
- [ ] Test 8: Key alias storage and retrieval
- [ ] Test 9: Automatic file visibility
- [ ] Test 10: Configuration customization

**v1.3.1 - Key Generation:**
- [ ] Test 1: Keys actually created on card
- [ ] Test 2: Encryption/decryption works after key generation
- [ ] Test 3: APDU commands logged (not subprocess)
- [ ] Test 4: Error handling works correctly

**v1.3.0 - PFX Import:**
- [ ] Test 5: PFX import option not shown

**v1.2.0 - PIN Change:**
- [ ] Test 6: PIN change succeeds end-to-end
- [ ] Test 7: PIN tracking after key generation

### Troubleshooting Test Failures

**If key generation appears to succeed but encryption fails:**
1. Check `gpg --card-status` - are keys actually present?
2. Check debug log for `SW=6A88` errors
3. Verify you're running v1.3.1 or later
4. Try factory-reset and regenerate

**If PIN change fails:**
1. Verify GPG is installed and in PATH
2. Check debug log for GPG command output
3. Ensure card is not locked (retry counter > 0)
4. Try manual GPG PIN change to verify card works

**If tests fail with "card not found":**
1. Verify ATR matches: `3B D5 18 FF 81 B1 FE 45 1F C3 80 73 C8 21 10 6F`
2. Check Device Manager for smart card reader
3. Try different USB port
4. Restart PC/SC service: `net stop SCardSvr && net start SCardSvr`

### Reporting Test Results

When reporting test results, include:

1. **Test environment:**
   - Windows version (10/11)
   - AEPGP Context Menu version
   - Card ATR
   - GPG version

2. **Test results:**
   - Which tests passed/failed
   - Exact error messages
   - Screenshots of errors

3. **Debug logs:**
   - Attach or paste relevant sections from `%TEMP%\aepgp_debug.log`
   - Include timestamps

4. **Steps to reproduce failures:**
   - Detailed step-by-step instructions
   - Starting state of card (factory reset, keys present, etc.)

---

## Version History

### Version 1.3.2 (2026-01-08)
- ✨ **NEW:** Automatic file visibility management - .enc files hidden when card not present
- ✨ **NEW:** Background visibility watcher service (runs at user logon)
- ✨ **NEW:** Key alias feature - store and retrieve human-readable key pair names on card
- ✨ **NEW:** Improved key generation with alias prompts and existing key detection
- 🔧 **IMPROVED:** Better confirmation dialogs when overwriting existing keys
- 🔧 **IMPROVED:** Card presence check before decryption operations
- 📝 **DOCUMENTATION:** Updated main README with visibility watcher configuration
- 📝 **DOCUMENTATION:** Added .gitignore rules for Outlook integration files

### Version 1.3.1 (2026-01-01)
- 🐛 **FIXED:** Key generation using direct APDU commands
- 🐛 **FIXED:** Encryption now works correctly after key generation
- 🔧 **IMPROVED:** Removed broken subprocess approach to key generation
- 🔧 **IMPROVED:** Better error messages for missing keys
- 📝 **DOCUMENTATION:** Comprehensive bug fix documentation

### Version 1.3.0 (2026-01-01)
- 🔧 **CHANGED:** Disabled incomplete PFX import feature
- 📝 **DOCUMENTATION:** Added technical notes on buffer limitations

### Version 1.2.0 (2025-12-31)
- ✨ **NEW:** Automated PIN change functionality with GPG integration
- ✨ **NEW:** Hybrid PIN change method (APDU verification + GPG passwd)
- 🔧 **IMPROVED:** Automatic GPG process management (kill scdaemon/gpg-agent)
- 🔧 **IMPROVED:** Dynamic PIN tracking in test suite
- 🐛 **FIXED:** GPG smart card lock issue preventing card access
- 🐛 **FIXED:** PIN verification failures after key generation
- 🐛 **FIXED:** PIN change compatibility across OpenPGP cards

### Version 1.1.0
- **NEW:** RSA+AES hybrid encryption (no GPG keyring required)
- **NEW:** Direct APDU communication with AEPGP card
- **NEW:** Generate keys on card via context menu
- **NEW:** Debug logging to %TEMP%\aepgp_debug.log
- **IMPROVED:** Decrypt restores original file extensions
- **CHANGED:** .enc file extension instead of .gpg
- **CHANGED:** No dependency on GPG keyring

### Version 1.0.0
- Initial release
- Basic GPG-based encryption/decryption
- AmbiSecure token detection
- AEPGP branding
- Context menu integration

---

## Uninstallation

### Via Windows Settings

1. Windows Settings → Apps
2. Find "AEPGP Context Menu"
3. Click "Uninstall"
4. Confirm uninstallation

### Silent Uninstall

```cmd
msiexec /x AEPGP_Context_Menu-1.3.1-win64.msi /quiet /norestart
```

### Manual Uninstall

1. Open `windows_context_menu` folder
2. Right-click `uninstall_menu.py` → "Run as administrator"
3. Or via Command Prompt (as Administrator):
   ```cmd
   python uninstall_menu.py
   ```

---

## Technical Notes

### PFX Import Status

The PFX import feature is currently **disabled** due to SmartPGP applet buffer limitations:

- SmartPGP's internal buffer is limited to 1280 bytes
- RSA-2048 key import requires ~1843 bytes
- Command chaining fails at chunk 3 with error 6581 (SW_MEMORY_FAILURE)
- Solution requires rebuilding SmartPGP applet with larger buffer (2048 bytes)

For details, see: `README-APDU.md` in the original documentation.

### Key Generation Fix (v1.3.1)

The key generation handler was completely rewritten to use direct APDU commands:

**Previous Issue:**
- Used subprocess to call `python -m smartpgp.highlevel generate-key`
- This module had no CLI implementation
- Commands appeared to succeed but didn't generate keys
- Resulted in "No keys on card" errors

**Solution:**
- Direct APDU communication via pyscard
- Proper admin PIN verification
- Correct GENERATE KEY command structure
- GET RESPONSE handling for large responses

For details, see: `BUGFIX_KEY_GENERATION.md` in the original documentation.

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

**For Issues:**
- Check debug log: `%TEMP%\aepgp_debug.log`
- Review this documentation
- Contact your AEPGP administrator

**For SmartPGP Card Issues:**
- Visit: https://github.com/ANSSI-FR/SmartPGP

**For Library Issues:**
- pyscard: https://pyscard.sourceforge.io/
- cryptography: https://cryptography.io/

### Reporting Issues

When reporting issues, include:
- Windows version (10 or 11)
- AEPGP Context Menu version
- Card ATR (from debug log)
- Error messages (exact text)
- Relevant debug log entries
- Steps to reproduce

---

**AEPGP Context Menu v1.3.1 - Professional Windows Integration for AEPGP Smart Cards**
