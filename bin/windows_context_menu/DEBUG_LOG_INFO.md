# AEPGP Debug Logging

## Overview

The AEPGP Context Menu tools now include comprehensive debug logging to help trace issues and troubleshoot problems.

## Debug Log Location

**Windows:** `C:\Users\<YourUsername>\AppData\Local\Temp\aepgp_debug.log`

**Quick Access:**
1. Press `Win + R`
2. Type: `%TEMP%`
3. Press Enter
4. Look for `aepgp_debug.log`

## What Gets Logged

Every time you use "Encrypt with AEPGP" or "Decrypt with AEPGP", the following information is logged:

### Operation Information
- **Timestamp** - Exact time of operation (millisecond precision)
- **Operation Type** - Encryption or Decryption
- **File Path** - The file being processed
- **File Size** - Size in bytes

### System Information
- Python version
- Platform (Windows version)
- Working directory
- List of smart card readers detected

### Card Detection
- Number of readers found
- Whether card was detected
- Card ATR (Answer To Reset) in hexadecimal
- Reader name where card was found

### GPG Execution
- Full GPG command executed
- GPG return code (0 = success)
- GPG stdout output
- GPG stderr output (errors/warnings)

### Errors and Exceptions
- Error messages
- Exception types
- Full stack traces
- Context information

## Example Log Entry

```
================================================================================
[2025-12-30 15:39:23.261] [INFO]
Starting Encryption operation
File: C:\Users\Neel\Documents\test.txt
================================================================================

================================================================================
[2025-12-30 15:39:23.265] [DEBUG]
System Information:
  Python: 3.11.9
  Platform: win32
  Working Dir: C:\Program Files\AEPGP Context Menu
  Smart Card Readers: 2
    1. Gemalto USB Smart Card Reader 0
    2. Windows Hello for Business 1
================================================================================

================================================================================
[2025-12-30 15:39:23.270] [INFO]
File exists, size: 1024 bytes
================================================================================

================================================================================
[2025-12-30 15:39:23.275] [DEBUG]
Card Detection:
  Readers found: 1
  Card detected: True
  ATR: 3B D5 18 FF 81 91 FE 1F C3 80 73 C8 21 10 0A
================================================================================

================================================================================
[2025-12-30 15:39:23.280] [INFO]
Found GnuPG at: C:\Program Files\GnuPG\bin\gpg.exe
================================================================================

================================================================================
[2025-12-30 15:39:23.285] [INFO]
Executing GPG command: gpg --armor --output test.txt.gpg --encrypt --sign test.txt
================================================================================

================================================================================
[2025-12-30 15:39:45.123] [INFO]
Encryption operation completed successfully
================================================================================
```

## Log Management

### Automatic Rotation
- Log files are automatically rotated when they exceed **5MB**
- Old log is renamed to `aepgp_debug.log.old`
- New log file starts fresh

### Manual Cleanup
To manually delete the log:
1. Close all AEPGP operations
2. Navigate to `%TEMP%`
3. Delete `aepgp_debug.log`

### Privacy Note
The debug log contains:
- ✅ File paths you encrypted/decrypted
- ✅ System information
- ✅ Card ATR (hardware identifier)
- ❌ NO PIN codes
- ❌ NO file contents
- ❌ NO encryption keys

## Using the Debug Log for Troubleshooting

### If Encryption/Decryption Fails

1. **Find the log file:**
   - Open `%TEMP%\aepgp_debug.log`

2. **Look for the most recent operation:**
   - Scroll to the bottom of the file
   - Look for timestamps matching your operation

3. **Check for errors:**
   - Look for `[ERROR]` entries
   - Check GPG return codes (non-zero = error)
   - Read error messages

4. **Common Issues:**

   **Card not detected:**
   ```
   [ERROR]
   Card detection failed: AEPGP card not found
   ```
   → Check ATR list, may need to add your card

   **GPG not found:**
   ```
   [ERROR]
   GnuPG not found on system
   ```
   → Install GnuPG or Gpg4win

   **GPG execution error:**
   ```
   [ERROR]
   GPG encryption failed: gpg: decryption failed: No secret key
   ```
   → Wrong card or key not available

### Sharing Logs for Support

If you need help:
1. Reproduce the issue
2. Locate the log file (`%TEMP%\aepgp_debug.log`)
3. Copy the relevant log entries (last operation)
4. **Remove any sensitive file paths** before sharing
5. Share with support or open a GitHub issue

## Disabling Logging

To disable logging, edit the handler files:
- `bin\windows_context_menu\handlers\encrypt_handler.py`
- `bin\windows_context_menu\handlers\decrypt_handler.py`

Comment out the line:
```python
# logger = get_logger()
```

## Log Levels

- **DEBUG** - Detailed diagnostic information
- **INFO** - General informational messages
- **WARNING** - Warning messages, operation continues
- **ERROR** - Error messages, operation failed

---

**Log File:** `%TEMP%\aepgp_debug.log`
**Max Size:** 5MB (auto-rotated)
**Retention:** Manual cleanup required
