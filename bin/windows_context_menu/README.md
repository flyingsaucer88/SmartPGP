# SmartPGP Windows Context Menu Integration

This package provides Windows Explorer context menu integration for encrypting and decrypting files using your SmartPGP card.

## Features

- **Right-click to Encrypt**: Right-click any file and select "Encrypt with SmartPGP"
- **Right-click to Decrypt**: Right-click encrypted files (.gpg, .pgp, .asc) and select "Decrypt with SmartPGP"
- **Automatic Card Detection**: Checks for SmartPGP card presence before operations
- **User-Friendly Dialogs**: Clear error messages and success notifications
- **Secure**: Uses GnuPG with your SmartPGP card for all cryptographic operations

## Requirements

### Hardware
- SmartPGP-compatible JavaCard smart card
- USB smart card reader

### Software
- **Windows 10 or Windows 11**
- **Python 3.7 or later** (with pip)
- **GnuPG** (gpg.exe) - Download from:
  - [GnuPG Official](https://www.gnupg.org/download/)
  - [Gpg4win](https://www.gpg4win.org/) (recommended for Windows users)
- **pyscard** Python library (for smart card communication)

## Installation

### Step 1: Install Prerequisites

1. **Install Python** (if not already installed):
   - Download from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"

2. **Install GnuPG**:
   - Download and install [Gpg4win](https://www.gpg4win.org/)
   - Or download [GnuPG](https://www.gnupg.org/download/)

3. **Install pyscard library**:
   ```cmd
   pip install pyscard
   ```

### Step 2: Set Up Your SmartPGP Card

Before using the context menu, you need to configure your SmartPGP card with GnuPG:

1. Insert your SmartPGP card into the USB reader

2. Check that GnuPG can see your card:
   ```cmd
   gpg --card-status
   ```

3. If you haven't set up keys on your card yet, generate or import them:
   ```cmd
   gpg --card-edit
   > admin
   > generate
   ```

   Follow the prompts to generate a new key pair on your card.

4. (Optional) If you have existing keys, you can move them to the card:
   ```cmd
   gpg --edit-key YOUR_KEY_ID
   > keytocard
   ```

### Step 3: Install the Context Menu

1. Open the `windows_context_menu` folder in Windows Explorer

2. **Right-click** `install_menu.py` and select **"Run as administrator"**

   Or open Command Prompt as Administrator and run:
   ```cmd
   python install_menu.py
   ```

3. If prompted for elevation (UAC), click **Yes**

4. Wait for the installation to complete. You should see:
   ```
   ✓ Installed 'Encrypt with SmartPGP' menu item
   ✓ Installed 'Decrypt with SmartPGP' for .gpg files
   ✓ Installed 'Decrypt with SmartPGP' for .pgp files
   ✓ Installed 'Decrypt with SmartPGP' for .asc files
   Installation completed successfully! ✓
   ```

5. Press Enter to exit

## Usage

### Encrypting Files

1. **Insert your SmartPGP card** into the USB reader

2. **Right-click any file** in Windows Explorer

3. Select **"Encrypt with SmartPGP"**
   - On Windows 11: Click "Show more options" first, then select "Encrypt with SmartPGP"
   - Or use **SHIFT+Right-click** to access the menu directly

4. **Enter your card PIN** when prompted by the pinentry dialog

5. The encrypted file will be created with a `.gpg` extension in the same folder

### Decrypting Files

1. **Insert your SmartPGP card** into the USB reader

2. **Right-click an encrypted file** (.gpg, .pgp, or .asc)

3. Select **"Decrypt with SmartPGP"**
   - On Windows 11: Click "Show more options" first

4. **Enter your card PIN** when prompted

5. The decrypted file will be created (without the .gpg extension) in the same folder

## Troubleshooting

### "SmartPGP card not found" Error

**Problem**: The context menu handler cannot detect your SmartPGP card.

**Solutions**:
- Make sure your smart card reader is connected to your PC
- Insert your SmartPGP card into the reader
- Try removing and re-inserting the card
- Check if Windows recognizes the reader in Device Manager
- Test with: `gpg --card-status` in Command Prompt

### "GnuPG not found" Error

**Problem**: The context menu handler cannot find gpg.exe.

**Solutions**:
- Install GnuPG from [gpg4win.org](https://www.gpg4win.org/)
- Make sure GnuPG is added to your system PATH
- Test with: `gpg --version` in Command Prompt

### "Encryption/Decryption Failed" Error

**Problem**: GnuPG cannot perform the operation.

**Possible causes**:
- Wrong PIN entered (card may be locked after 3 failed attempts)
- File is corrupted
- Card is not properly initialized with keys
- Trying to decrypt a file that wasn't encrypted for your key

**Solutions**:
- Verify your card status: `gpg --card-status`
- Check your PIN retry counter
- If PIN is locked, you may need to reset the card (see SmartPGP documentation)
- For decryption, ensure the file was encrypted for your public key

### Context Menu Items Don't Appear

**Problem**: Right-click menu doesn't show SmartPGP options.

**Solutions**:

1. **On Windows 11**: The options appear in "Show more options" (legacy context menu)
   - Right-click the file → Click "Show more options"
   - Or use SHIFT+Right-click to directly access the full menu

2. **Re-run the installer**:
   - Make sure you run `install_menu.py` as Administrator
   - Check for error messages during installation

3. **Restart Windows Explorer**:
   - Open Task Manager (Ctrl+Shift+Esc)
   - Find "Windows Explorer" in the Processes tab
   - Right-click → Restart

4. **Verify registry entries**:
   - Open Registry Editor (regedit)
   - Check: `HKEY_CLASSES_ROOT\*\shell\SmartPGP.Encrypt`
   - Check: `HKEY_CLASSES_ROOT\.gpg\shell\SmartPGP.Decrypt`

### Python Import Errors

**Problem**: "ModuleNotFoundError: No module named 'smartcard'"

**Solution**:
```cmd
pip install pyscard
```

If using multiple Python installations, make sure to install for the correct Python version:
```cmd
py -3 -m pip install pyscard
```

## Uninstallation

To remove the SmartPGP context menu items:

1. Open the `windows_context_menu` folder

2. **Right-click** `uninstall_menu.py` and select **"Run as administrator"**

   Or open Command Prompt as Administrator and run:
   ```cmd
   python uninstall_menu.py
   ```

3. Confirm the uninstallation when prompted

4. Wait for completion and press Enter to exit

## Technical Details

### How It Works

1. **Registry-Based Integration**: The installer creates Windows Registry entries in `HKEY_CLASSES_ROOT` that add menu items to the Explorer context menu

2. **Handler Scripts**: When you click a menu item, Windows executes the corresponding Python handler script:
   - `encrypt_handler.py` - For encryption
   - `decrypt_handler.py` - For decryption

3. **Card Detection**: The handler script uses `pyscard` to detect if a SmartPGP card is present in any connected reader

4. **GnuPG Integration**: The actual encryption/decryption is performed by GnuPG (gpg.exe), which communicates with your SmartPGP card via the PC/SC interface

### File Structure

```
windows_context_menu/
├── handlers/
│   ├── card_utils.py          # Smart card detection utilities
│   ├── encrypt_handler.py     # Encryption handler
│   └── decrypt_handler.py     # Decryption handler
├── install_menu.py             # Installer script
├── uninstall_menu.py           # Uninstaller script
└── README.md                   # This file
```

### Registry Entries Created

**For Encryption** (all files):
```
HKEY_CLASSES_ROOT\*\shell\SmartPGP.Encrypt
    (Default) = "Encrypt with SmartPGP"
    \command
        (Default) = "C:\...\pythonw.exe" "C:\...\encrypt_handler.py" "%1"
```

**For Decryption** (.gpg, .pgp, .asc files):
```
HKEY_CLASSES_ROOT\.gpg\shell\SmartPGP.Decrypt
    (Default) = "Decrypt with SmartPGP"
    \command
        (Default) = "C:\...\pythonw.exe" "C:\...\decrypt_handler.py" "%1"
```

### Security Considerations

- **PIN Entry**: Your card PIN is entered via GnuPG's pinentry program, not through the context menu scripts
- **No PIN Storage**: The scripts never see or store your PIN
- **Card Communication**: All cryptographic operations occur on the smart card itself
- **Private Keys**: Your private keys never leave the smart card

## Advanced Configuration

### Using a Different Python Installation

If you have multiple Python installations, edit the installed registry entries to point to your preferred Python:

1. Open Registry Editor (regedit)
2. Navigate to the command key (see "Registry Entries Created" above)
3. Edit the path to python.exe/pythonw.exe

### Customizing Menu Text

Edit `install_menu.py` and change these lines before installation:

```python
winreg.SetValue(key, "", winreg.REG_SZ, "Your Custom Text Here")
```

### Adding Menu Icons

Uncomment and customize the icon lines in `install_menu.py`:

```python
winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, r"C:\path\to\your\icon.ico")
```

## Known Limitations

- **Windows 11**: Context menu items appear in "Show more options" (legacy menu), not in the new compact menu
- **Multiple Cards**: If multiple SmartPGP cards are present, the first one found is used
- **File Size**: Very large files may take a long time to encrypt/decrypt (limited by GnuPG performance)
- **Binary Output**: Encrypted files are in binary format by default (remove `--armor` flag in handler scripts for ASCII-armored output)

## Support

For issues related to:
- **SmartPGP card**: See the main [SmartPGP README](../../README.md)
- **GnuPG**: Visit [GnuPG documentation](https://www.gnupg.org/documentation/)
- **pyscard**: Visit [pyscard documentation](https://pyscard.sourceforge.io/)
- **This context menu integration**: Open an issue on the SmartPGP GitHub repository

## License

This context menu integration is part of the SmartPGP project and is licensed under the same terms (GNU General Public License v2).

## Credits

- SmartPGP JavaCard implementation: ANSSI (French National Cybersecurity Agency)
- Context menu integration: Developed for SmartPGP users on Windows
- Uses: GnuPG, pyscard, Python standard library
