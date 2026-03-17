# AEPGP Context Menu - Enhancement Roadmap

**Last Updated:** 2026-01-08
**Current Version:** 1.3.1

---

## Priority 1 - Critical Features

### 1. PFX Import Functionality
**Status:** ❌ Disabled (Blocked by SmartPGP applet limitation)
**Priority:** High
**Effort:** Large

**Description:**
Enable users to import RSA-2048 private keys from PFX (PKCS#12) files to SmartPGP cards.

**Current Blocker:**
- SmartPGP applet has `INTERNAL_BUFFER_MAX_LENGTH` of 1280 bytes
- RSA-2048 key import requires ~1843 bytes
- Command chaining fails at chunk 3 with error 6581 (SW_MEMORY_FAILURE)

**Required Steps:**
1. [ ] Rebuild SmartPGP applet with larger buffer (2048 bytes)
   - Edit: `SmartPGP/src/fr/anssi/smartpgp/Constants.java:29`
   - Change: `INTERNAL_BUFFER_MAX_LENGTH = (short)0x500;` → `(short)0x800;`
   - Build: `ant` in SmartPGP directory
   - Output: `SmartPGPApplet.cap`

2. [ ] Install modified applet to AEPGP cards
   ```cmd
   gp --delete D276000124010304AEPGPV1.0
   gp --install SmartPGPApplet.cap
   ```

3. [ ] Re-enable PFX import handler
   - Uncomment registry entries in `install_menu.py`
   - Test with multiple PFX files

4. [ ] Verify mathematical correctness
   - Test p < q constraint handling
   - Test coefficient calculation (q^-1 mod p)
   - Test CRT exponent swapping

5. [ ] Add comprehensive error handling
   - Invalid PFX password
   - Unsupported key sizes (non-RSA-2048)
   - Corrupted PFX files

**Technical Notes:**
- Implementation exists but disabled (v1.2.19-v1.2.28 attempts documented)
- Mathematical verification passed in v1.2.27
- Structure validation passed (BER-TLV format correct)
- Only buffer size preventing success

**References:**
- See: `README.md` - Technical Notes section
- Original debugging: Was in `PFX_IMPORT_DEBUGGING_SUMMARY.md`
- APDU details: Was in `README-APDU.md`

---

## Priority 2 - User Experience

### 2. Windows 11 Modern Context Menu Integration
**Status:** ⚠️ Partial (works via "Show more options")
**Priority:** Medium
**Effort:** Medium

**Description:**
Add AEPGP menu items directly to Windows 11's modern right-click context menu.

**Required Steps:**
1. [ ] Research Windows 11 Shell Extensions API
2. [ ] Implement COM-based shell extension (C++/C#)
3. [ ] Register sparse package for manifest
4. [ ] Add icons for modern context menu
5. [ ] Test on Windows 11 22H2 and later
6. [ ] Maintain backward compatibility with Windows 10

**Technical Notes:**
- Current implementation uses legacy context menu (still works)
- Modern menu requires different registration method
- May need signed package for distribution

---

### 3. File Visibility Enhancements
**Status:** ⚠️ Base feature completed, enhancements pending
**Priority:** Medium
**Effort:** Small to Medium

**Description:**
Enhance the existing file visibility management system with additional features.

**Completed (v1.3.2):**
- ✅ Background visibility watcher service
- ✅ Automatic hide/show based on card presence
- ✅ Configurable via environment variables

**Future Enhancements:**
- [ ] **GUI for configuration** (instead of environment variables)
  - Visual interface to set watch paths
  - Adjust polling/rescan intervals
  - View current watcher status

- [ ] **System tray icon with status indicator**
  - Show card present/absent status
  - Quick access to pause/resume watcher
  - Right-click menu for manual sync

- [ ] **Manual sync trigger option**
  - Context menu: "Sync .enc file visibility"
  - Keyboard shortcut support

- [ ] **Statistics display**
  - Count of files hidden/shown
  - Last sync timestamp
  - Error count and details

- [ ] **Enhanced Card Verification** ⭐ PRIORITY
  - Current: Visibility based on ATR match alone
  - Proposed: Send custom APDU command and verify expected response
  - Benefits: More secure card identification, prevents spoofing
  - Prerequisites:
    1. Update SmartPGP applet to support proprietary verification command
    2. Define command structure (e.g., `00 XX XX XX` → expected response)
    3. Update `card_utils.py` to use both ATR and command verification
    4. Update `visibility_watcher.py` to use enhanced verification
  - Implementation notes:
    - Fall back to ATR-only if proprietary command fails (backward compatibility)
    - Log verification method used for debugging
    - Add configuration option to require proprietary verification

---

### 4. Key Alias Enhancements
**Status:** ⚠️ Base feature completed, enhancements pending
**Priority:** Low
**Effort:** Small

**Description:**
Enhance the existing key alias management with multi-card support and metadata.

**Completed (v1.3.2):**
- ✅ Store alias in Private DO 0x0102 on card
- ✅ Read/write alias functionality
- ✅ Prompt during key generation

**Future Enhancements:**
- [ ] **Multi-card alias listing**
  - Enumerate all available cards with their aliases
  - Quick card selection by alias

- [ ] **Alias export/import**
  - Backup alias mappings to file
  - Restore from backup
  - Share alias configurations

- [ ] **Extended metadata storage**
  - Creation date/time
  - Key purpose (encryption, signing, auth)
  - Owner contact information
  - Notes field

---

### 5. GUI Configuration Tool
**Status:** ❌ Not Started
**Priority:** Low
**Effort:** Medium

**Description:**
Create a GUI application for managing AEPGP settings and card operations.

**Proposed Features:**
- [ ] Card status display (ATR, key info, PIN retry counter)
- [ ] One-click key generation
- [ ] PIN change interface (avoid command line)
- [ ] View encryption/decryption logs
- [ ] Configure default encryption settings
- [ ] Test card connectivity

**Technical Notes:**
- Could use Python + tkinter (matches existing stack)
- Or create native Windows app (C# WPF/WinForms)
- Should integrate with existing handlers

---

### 4. Batch File Operations
**Status:** ❌ Not Started
**Priority:** Low
**Effort:** Small

**Description:**
Support encrypting/decrypting multiple files at once.

**Required Steps:**
1. [ ] Accept multiple file paths in handlers
2. [ ] Show progress bar for batch operations
3. [ ] Handle errors gracefully (continue on failure)
4. [ ] Generate summary report
5. [ ] Add "Encrypt All" option in folder context menu

---

## Priority 3 - Security & Reliability

### 5. Enhanced PIN Entry Security
**Status:** ⚠️ Uses tkinter dialogs
**Priority:** Medium
**Effort:** Small

**Description:**
Use GPG's pinentry program instead of custom tkinter dialogs for better security.

**Required Steps:**
1. [ ] Detect installed pinentry program
2. [ ] Implement pinentry protocol communication
3. [ ] Fallback to tkinter if pinentry unavailable
4. [ ] Add configuration option for PIN entry method

**Security Benefits:**
- Trusted input method (used by GPG)
- Better protection against keyloggers
- Consistent UX with other GPG tools

---

### 6. Key Backup and Recovery
**Status:** ❌ Not Started
**Priority:** Medium
**Effort:** Medium

**Description:**
Provide secure backup mechanism for encryption keys.

**Proposed Features:**
- [ ] Export public key to file
- [ ] Generate QR code with public key
- [ ] Backup encrypted private key (off-card storage)
- [ ] Restore from backup to new card
- [ ] Support for multiple backup slots

**Security Considerations:**
- Private key export requires card support
- SmartPGP may not support private key export
- Alternative: Use key generation with seed backup

---

### 7. Automated Testing Suite
**Status:** ⚠️ Basic test script exists
**Priority:** Medium
**Effort:** Medium

**Description:**
Comprehensive automated testing for all functionality.

**Required Steps:**
1. [ ] Create test PFX files (various key sizes)
2. [ ] Create test encrypted files
3. [ ] Automated card detection tests
4. [ ] Key generation verification tests
5. [ ] Encryption/decryption round-trip tests
6. [ ] PIN change tests with state tracking
7. [ ] Error condition tests (wrong PIN, missing card, etc.)
8. [ ] Regression tests for bug fixes

**Current State:**
- `test_all_features.py` exists but needs expansion
- Tests documented in v1.2.0 release notes

---

## Priority 4 - Advanced Features

### 8. Support for Additional Key Types
**Status:** ❌ Not Started
**Priority:** Low
**Effort:** Large

**Description:**
Support importing/using different key types beyond RSA-2048.

**Proposed Support:**
- [ ] RSA-4096 keys (requires larger buffer)
- [ ] ECDSA keys (P-256, P-384, P-521)
- [ ] EdDSA keys (Ed25519)
- [ ] Hybrid encryption with different algorithms

**Technical Notes:**
- SmartPGP card capabilities need verification
- May require applet modifications
- Different APDU commands for different key types

---

### 9. File Signing Support
**Status:** ❌ Not Started
**Priority:** Low
**Effort:** Medium

**Description:**
Add digital signature functionality using card's signing key.

**Proposed Features:**
- [ ] Sign files with card
- [ ] Verify signatures
- [ ] Context menu: "Sign with AEPGP"
- [ ] Context menu: "Verify AEPGP Signature"
- [ ] Support detached and embedded signatures

---

### 10. Cloud Storage Integration
**Status:** ❌ Not Started
**Priority:** Low
**Effort:** Large

**Description:**
Encrypt files before uploading to cloud storage.

**Proposed Features:**
- [ ] Auto-encrypt on cloud folder sync
- [ ] Decrypt on download
- [ ] Support OneDrive, Google Drive, Dropbox
- [ ] Transparent encryption layer

**Security Considerations:**
- Key management for multiple devices
- PIN entry on automated operations
- Secure key sharing between authorized devices

---

## Priority 5 - Distribution & Deployment

### 11. Code Signing Certificate
**Status:** ❌ Not Started
**Priority:** Medium
**Effort:** Small (cost + time)

**Description:**
Sign installer and executables with code signing certificate.

**Benefits:**
- Removes Windows SmartScreen warnings
- Establishes trust with users
- Professional appearance
- Required for some enterprise deployments

**Required Steps:**
1. [ ] Purchase code signing certificate (EV recommended)
2. [ ] Sign MSI installer
3. [ ] Sign all .exe files
4. [ ] Update build scripts to auto-sign
5. [ ] Timestamp signatures for long-term validity

---

### 12. Automated Build Pipeline
**Status:** ❌ Not Started
**Priority:** Low
**Effort:** Medium

**Description:**
Set up CI/CD for automated building and testing.

**Proposed Features:**
- [ ] GitHub Actions workflow
- [ ] Automated version bumping
- [ ] Build on commit to main branch
- [ ] Run test suite automatically
- [ ] Generate release artifacts
- [ ] Create GitHub releases automatically

---

### 13. Multi-Language Support
**Status:** ❌ English only
**Priority:** Low
**Effort:** Medium

**Description:**
Internationalization (i18n) support for multiple languages.

**Proposed Languages:**
- [ ] French (SmartPGP origin)
- [ ] German
- [ ] Spanish
- [ ] Japanese
- [ ] Chinese

**Required Steps:**
1. [ ] Extract all user-facing strings
2. [ ] Create translation framework
3. [ ] Generate translation files (.po/.pot)
4. [ ] Translate to target languages
5. [ ] Add language selection option

---

## Bug Fixes & Improvements

### Known Issues

1. **GPG Agent Lock** ✅ FIXED in v1.2.0
   - Automatic termination of GPG processes
   - No longer blocks card access

2. **Key Generation via Subprocess** ✅ FIXED in v1.3.1
   - Now uses direct APDU commands
   - Reliable key generation

3. **PIN Tracking** ✅ FIXED in v1.2.0
   - Dynamic PIN tracking throughout lifecycle
   - Handles factory reset after key generation

### Future Improvements

- [ ] Reduce installer size (currently ~20-35 MB)
- [ ] Faster encryption for large files (>100 MB)
- [ ] Better progress indication during operations
- [ ] Retry logic for transient card communication errors
- [ ] Cache card ATR to avoid repeated detection
- [ ] Improve error messages with actionable suggestions

---

## Documentation Improvements

### User Documentation
- [ ] Video tutorials for common operations
- [ ] Troubleshooting flowcharts
- [ ] FAQ section expansion
- [ ] Quick reference card (printable)

### Developer Documentation
- [ ] API documentation for handlers
- [ ] APDU command reference (complete)
- [ ] Architecture diagrams
- [ ] Contributing guidelines
- [ ] Code style guide

### Deployment Documentation
- [ ] Enterprise deployment guide (Group Policy)
- [ ] Silent installation parameters
- [ ] Network deployment scenarios
- [ ] Multi-user configuration

---

## Completed Items ✅

### Version 1.3.2 (2026-01-08)
- ✅ Automatic file visibility management (.enc files hidden when card not present)
- ✅ Background visibility watcher service (runs at user logon)
- ✅ Key alias feature - store human-readable key pair names on card
- ✅ Improved key generation with alias prompts and existing key detection
- ✅ Better confirmation dialogs when overwriting existing keys
- ✅ Card presence check before decryption operations
- ✅ Configuration via environment variables (watch paths, polling intervals)
- ✅ Added .gitignore rules for Outlook integration files

### Version 1.3.1 (2026-01-01)
- ✅ Fixed key generation using direct APDU commands
- ✅ Removed broken subprocess approach
- ✅ Improved error messages for missing keys

### Version 1.3.0 (2026-01-01)
- ✅ Disabled incomplete PFX import (until applet rebuilt)

### Version 1.2.0 (2025-12-31)
- ✅ Automated PIN change with GPG integration
- ✅ GPG process management (kill scdaemon/agent)
- ✅ Dynamic PIN tracking in test suite
- ✅ Fixed GPG smart card lock issue

### Version 1.1.0
- ✅ RSA+AES hybrid encryption
- ✅ Direct APDU communication
- ✅ Generate keys on card
- ✅ Debug logging

---

## Contributing

Want to help? Pick an item from the list above and:

1. Comment on the issue or create one
2. Fork the repository
3. Create a feature branch
4. Submit a pull request

For questions or discussions, contact the project maintainers.

---

## Version Planning

### v1.4.0 (Planned)
- PFX import re-enablement (pending applet rebuild)
- Enhanced error handling
- Improved logging

### v1.5.0 (Planned)
- Windows 11 modern context menu
- GUI configuration tool
- Batch operations

### v2.0.0 (Future)
- Multiple key type support
- File signing functionality
- Cloud storage integration

---

**Note:** Priorities and timelines are subject to change based on user feedback and technical constraints.
