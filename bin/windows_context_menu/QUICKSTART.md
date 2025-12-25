# SmartPGP Context Menu - Quick Start Guide

## Installation (3 Easy Steps)

### 1. Install Prerequisites

- **Python 3.7+**: Download from [python.org](https://www.python.org/downloads/)
  - ✅ Check "Add Python to PATH" during installation

- **GnuPG**: Download from [gpg4win.org](https://www.gpg4win.org/)
  - This provides the `gpg.exe` command needed for encryption

### 2. Run the Installer

**Option A - Easy Way** (Recommended):
- Double-click `INSTALL.bat`
- Click "Yes" when prompted for Administrator privileges

**Option B - Manual Way**:
1. Open Command Prompt as Administrator
2. Run: `pip install pyscard`
3. Run: `python install_menu.py`

### 3. Set Up Your Card (First Time Only)

Insert your SmartPGP card and generate/import keys:

```cmd
gpg --card-edit
> admin
> generate
```

Follow the prompts to create your encryption key on the card.

## Usage

### Encrypt a File
1. Insert your SmartPGP card
2. Right-click any file → **"Encrypt with SmartPGP"**
   - Windows 11: Click "Show more options" first
3. Enter your card PIN when prompted
4. Encrypted file (`.gpg`) will be created

### Decrypt a File
1. Insert your SmartPGP card
2. Right-click the `.gpg` file → **"Decrypt with SmartPGP"**
   - Windows 11: Click "Show more options" first
3. Enter your card PIN when prompted
4. Decrypted file will be created

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Card not found" | Insert your SmartPGP card into the reader |
| "GnuPG not found" | Install GnuPG from gpg4win.org |
| "Module 'smartcard' not found" | Run: `pip install pyscard` |
| Menu items don't appear | On Windows 11, click "Show more options" |
| Wrong PIN entered | Card locks after 3 attempts - may need reset |

## Uninstall

- Double-click `UNINSTALL.bat`
- Or run: `python uninstall_menu.py` as Administrator

## Need Help?

See [README.md](README.md) for detailed documentation and troubleshooting.
