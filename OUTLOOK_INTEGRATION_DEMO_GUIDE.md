# 📧 Outlook Integration - Complete Testing Guide

**For Engineers New to SmartPGP Outlook Integration**

This guide will walk you through testing the complete Outlook integration on both Windows and macOS, for both Desktop Outlook and Outlook Web (Office 365).

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Setup Phase 1: Windows Testing](#setup-phase-1-windows-testing)
4. [Setup Phase 2: macOS Testing](#setup-phase-2-macos-testing)
5. [Testing Outlook Desktop (Windows)](#testing-outlook-desktop-windows)
6. [Testing Outlook Desktop (macOS)](#testing-outlook-desktop-macos)
7. [Testing Outlook Web with Browser Extension](#testing-outlook-web-with-browser-extension)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## Overview

### What You're Testing

You will test **4 scenarios**:

| # | Platform | Outlook Type | Integration | Expected Result |
|---|----------|--------------|-------------|-----------------|
| 1 | Windows | Desktop | Office Add-in | ✅ **Full encryption/decryption** |
| 2 | macOS | Desktop | Office Add-in | ✅ **Full encryption/decryption** |
| 3 | Windows/macOS | Web (O365) | **Browser Extension** | ✅ **Full encryption/decryption** |
| 4 | Windows/macOS | Web (O365) | **Browser Extension** | ✅ **Full encryption/decryption** |

**Two Integration Approaches**:
- **Office Add-in** (Scenarios 1-2): For Outlook Desktop - seamless ribbon integration, auto body access
- **Browser Extension** (Scenarios 3-4): For Outlook Web - bypasses browser CORS restrictions, manual copy/paste workflow

**All 4 scenarios now work!** The browser extension solves the previous Outlook Web limitation.

### Architecture

**Office Add-in (Desktop - Scenarios 1-2)**:
```
Outlook Desktop → Office Add-in (localhost:3000) → Helper (localhost:5555) → GPG → Card
```

**Browser Extension (Web - Scenarios 3-4)**:
```
Outlook Web → Browser Extension Widget → Helper (localhost:5555) → GPG → Card
                     ↑
            (Bypasses browser CORS via extension permissions)
```

**Common Helper Service** (used by both integrations):
```
Helper Service (HTTPS) — Windows or macOS at https://127.0.0.1:5555
    ↓
GPGME / GPG
    ↓
Smart Card Reader (USB/NFC)
    ↓
AEPGP SmartPGP Card
```

---

## 🎉 Demonstration Readiness Matrix

This matrix shows the current implementation status for all 4 test scenarios:

| Scenario | Platform | Outlook Type | Integration Method | Encrypt | Decrypt | UI Integration | Status |
|----------|----------|--------------|-------------------|---------|---------|----------------|--------|
| **1** | Windows | Desktop | Office Add-in | ✅ Works | ✅ Works | ✅ Ribbon buttons | ✅ **Fully Functional** |
| **2** | macOS | Desktop | Office Add-in | ✅ Works | ✅ Works | ✅ Ribbon buttons | ✅ **Fully Functional** |
| **3** | Windows | Web (O365) | Browser Extension | ✅ Works | ✅ Works | ⚠️ Floating widget | ✅ **Fully Functional** |
| **4** | macOS | Web (O365) | Browser Extension | ✅ Works | ✅ Works | ⚠️ Floating widget | ✅ **Fully Functional** |

### Component Status

| Component | Platform | Implementation | Status | Notes |
|-----------|----------|----------------|--------|-------|
| **Helper Service** | Windows | .NET 8 / ASP.NET Core / GpgmeSharp | ✅ Complete | HTTPS server on port 5555 |
| **Helper Service** | macOS | Swift / Vapor / NIOSSL / GPGME | ✅ Complete | HTTPS server on port 5555 |
| **Office Add-in** | Both | JavaScript / Office.js | ✅ Complete | For Desktop Outlook only |
| **Browser Extension** | Both | Chrome MV3 / Firefox MV2 | ✅ Complete | Bypasses CORS for Web scenarios |
| **Card Integration** | Both | GPGME + SmartPGP 3.4 | ✅ Complete | RSA-2048 encryption |
| **Certificate Setup** | Windows | Self-signed PFX | ✅ Complete | Trust setup required |
| **Certificate Setup** | macOS | Self-signed PFX | ✅ Complete | Keychain trust required |

### Integration Capabilities Comparison

| Capability | Office Add-in (Desktop) | Browser Extension (Web) |
|------------|------------------------|-------------------------|
| **Encryption** | ✅ Full support | ✅ Full support |
| **Decryption** | ✅ Full support | ✅ Full support |
| **Auto Body Access** | ✅ Direct API access | ❌ Manual copy/paste |
| **UI Integration** | ✅ Native ribbon buttons | ⚠️ Floating widget overlay |
| **Localhost Access** | ✅ Via Office.js | ✅ Via extension permissions |
| **CORS Bypass** | ✅ Office.js handles it | ✅ Extension host_permissions |
| **User Experience** | ⭐⭐⭐⭐⭐ Seamless | ⭐⭐⭐⭐ Manual workflow |
| **Browser Support** | N/A | Chrome, Edge, Firefox |

### Key Implementation Achievements

✅ **Windows Desktop (Scenario 1)**: Office Add-in with .NET 8 helper service - Full encryption/decryption via ribbon buttons
✅ **macOS Desktop (Scenario 2)**: Office Add-in with Swift/Vapor helper service - Full encryption/decryption via ribbon buttons
✅ **Windows Web (Scenario 3)**: Browser extension solves CORS limitation - Full encryption/decryption via floating widget
✅ **macOS Web (Scenario 4)**: Browser extension solves CORS limitation - Full encryption/decryption via floating widget

### Testing Readiness

All 4 scenarios are **ready for demonstration** with the following prerequisites:

1. ✅ Helper services build and run successfully on both platforms
2. ✅ Self-test endpoints verify card communication
3. ✅ Office Add-in loads and communicates with helper (Desktop scenarios)
4. ✅ Browser extension bypasses CORS restrictions (Web scenarios)
5. ✅ Certificate trust configured for HTTPS localhost access
6. ✅ AEPGP SmartPGP card properly initialized with encryption key
7. ✅ Card reader connected and recognized by system

### Known Limitations & Workarounds

| Limitation | Affects | Workaround |
|------------|---------|------------|
| Browser CORS restrictions | Web scenarios | ✅ **Solved** - Browser extension uses elevated permissions |
| Manual copy/paste required | Web scenarios | Expected - browser extension cannot auto-access Outlook Web DOM |
| Self-signed certificate warnings | All scenarios | User must trust certificate once during setup |
| Office Add-in not available in web | Web scenarios | Use browser extension instead (designed for this) |

---

## Prerequisites

### Hardware Requirements

- [ ] **AEPGP SmartPGP card** (AmbiSecure token)
- [ ] **Smart card reader** (USB CCID reader or NFC reader)
- [ ] **Windows computer** (for Windows testing) - Windows 10/11
- [ ] **macOS computer** (for macOS testing) - macOS 12+

### Software Requirements

#### For Windows Testing
- [ ] **Windows 10 or 11**
- [ ] **Outlook Desktop** installed (part of Microsoft 365 or standalone)
- [ ] **PowerShell 5.1+** (pre-installed on Windows 10/11)
- [ ] **.NET 8 SDK** - Download: https://dotnet.microsoft.com/download/dotnet/8.0
- [ ] **Gpg4win** - Download: https://gpg4win.org/download.html
- [ ] **Git for Windows** - Download: https://git-scm.com/download/win
- [ ] **Node.js 18+** - Download: https://nodejs.org/

#### For macOS Testing
- [ ] **macOS 12 (Monterey) or later**
- [ ] **Outlook Desktop** (Microsoft 365 for Mac)
- [ ] **Homebrew** - Install: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
- [ ] **Xcode Command Line Tools** - Run: `xcode-select --install`
- [ ] **Swift 5.9+** (comes with Xcode)
- [ ] **GnuPG** - Install: `brew install gnupg`
- [ ] **GPGME** - Install: `brew install gpgme`
- [ ] **Node.js 18+** - Install: `brew install node`

#### For Both Platforms
- [ ] **Web browser** (Chrome, Edge, Safari, or Firefox) for Outlook Web testing
- [ ] **Microsoft 365 account** with Outlook Web access (for web testing)
- [ ] **Administrator/sudo access** for certificate installation

### Knowledge Requirements

**You should know how to:**
- Open a terminal/command prompt
- Run basic commands
- Copy and paste text
- Edit configuration files (we'll guide you on what to change)

**You DON'T need to know:**
- Programming or coding
- How GPG works internally
- How smart cards work

---

## Setup Phase 1: Windows Testing

### Step 1.1: Clone the Repository

```powershell
# Open PowerShell (Right-click Start → Windows PowerShell)

# Navigate to your desired location
cd C:\Users\YourUsername\Documents

# Clone the repository
git clone https://github.com/yourusername/SmartPGP.git

# Navigate to the project
cd SmartPGP

# Switch to the outlookintegration branch
git checkout outlookintegration
```

### Step 1.2: Install Gpg4win

1. Download Gpg4win from: https://gpg4win.org/download.html
2. Run the installer
3. Select **GnuPG** component (required)
4. Select **Kleopatra** component (recommended - provides GUI)
5. Complete installation
6. Verify installation:
   ```powershell
   gpg --version
   ```
   You should see version information.

### Step 1.3: Configure Card Reader (Windows)

1. Connect your smart card reader to USB
2. Insert AEPGP SmartPGP card
3. Open PowerShell and run:
   ```powershell
   gpg --card-status
   ```
4. **First time setup**: You may be prompted to install drivers. Follow on-screen instructions.
5. Expected output should show:
   - Reader name
   - Application ID (starts with D2760001...)
   - Version information
   - Key slots (may be empty if new card)

**Troubleshooting**: If card is not detected:
- Try a different USB port
- Restart PC and try again
- Check Windows Device Manager → Smart Card Readers
- Install specific drivers from your card reader manufacturer

### Step 1.4: Build Windows Helper

```powershell
# Navigate to Windows helper directory
cd outlook_helper\windows\SmartPGP.OutlookHelper

# Restore NuGet packages
dotnet restore

# Build the project
dotnet build

# You should see: "Build succeeded"
```

**If build fails**:
- Ensure .NET 8 SDK is installed: `dotnet --version` should show 8.x.x
- Check for error messages and see [Troubleshooting](#troubleshooting)

### Step 1.5: Generate Certificates (Windows)

#### Generate Helper Certificate

```powershell
# Still in outlook_helper\windows\SmartPGP.OutlookHelper directory

# Create certs directory if it doesn't exist
New-Item -ItemType Directory -Force -Path certs

# Run certificate generation script
.\scripts\new-dev-cert.ps1

# You should see: "Certificate created at certs\localhost.pfx"
```

#### Generate Add-in Certificate

```powershell
# Navigate to add-in directory
cd ..\..\..\outlook_addin

# Create certs directory
New-Item -ItemType Directory -Force -Path certs

# Run certificate generation script
.\scripts\new-dev-cert.ps1

# You should see: "Certificate created at certs\addin-localhost.pfx"
```

#### Install Certificates to Windows Certificate Store

```powershell
# Import Helper certificate (requires Administrator privileges)
# Right-click PowerShell → "Run as Administrator"

# Import helper cert
$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2
$cert.Import("outlook_helper\windows\SmartPGP.OutlookHelper\certs\localhost.pfx", "change-me", "UserKeySet")
$store = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root", "CurrentUser")
$store.Open("ReadWrite")
$store.Add($cert)
$store.Close()
Write-Host "Helper certificate installed to Trusted Root" -ForegroundColor Green

# Import add-in cert
$cert2 = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2
$cert2.Import("outlook_addin\certs\addin-localhost.pfx", "change-me", "UserKeySet")
$store2 = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root", "CurrentUser")
$store2.Open("ReadWrite")
$store2.Add($cert2)
$store2.Close()
Write-Host "Add-in certificate installed to Trusted Root" -ForegroundColor Green
```

**Verify installation**:
1. Press `Win + R`, type `certmgr.msc`, press Enter
2. Expand **Trusted Root Certification Authorities** → **Certificates**
3. Look for certificates named "localhost" (you should see 2)

### Step 1.6: Configure Windows Helper

```powershell
# Navigate to Windows helper directory
cd outlook_helper\windows\SmartPGP.OutlookHelper

# Open configuration file in Notepad
notepad appsettings.json
```

**Verify the configuration** (should already be correct):
```json
{
  "SmartPgp": {
    "Port": 5555,
    "AllowedOrigins": [
      "https://localhost",
      "https://outlook.office.com",
      "https://outlook.live.com"
    ],
    "CertificatePath": "certs/localhost.pfx",
    "CertificatePassword": "change-me",
    "SignerId": ""
  }
}
```

**What this means**:
- **Port 5555**: The helper service runs on this port
- **AllowedOrigins**: Which websites can call the helper (Outlook Web, etc.)
- **CertificatePath**: Where the HTTPS certificate is located
- **CertificatePassword**: Password for the certificate
- **SignerId**: Leave empty for encryption-only (no signing)

Save and close if you made changes (you probably didn't need to).

### Step 1.7: Start Windows Helper

```powershell
# In outlook_helper\windows\SmartPGP.OutlookHelper directory

# Run the helper service
dotnet run
```

**Expected output**:
```
SmartPGP Outlook Helper for Windows
Listening on https://127.0.0.1:5555
Allowed origins: https://localhost, https://outlook.office.com, https://outlook.live.com

Available endpoints:
  POST /encrypt       - Encrypt plaintext for recipients
  POST /decrypt       - Decrypt PGP message
  POST /generate-keypair - Generate new keypair on card
  POST /change-pin    - Change card PIN
  POST /delete-keypair - Delete all keys (factory reset)
  GET  /card-status   - Get card status
  GET  /healthz       - Health check
```

**Keep this window open!** The service must keep running while you test.

### Step 1.8: Test Windows Helper (Self-Test)

**Open a NEW PowerShell window** (keep the helper running in the first window).

```powershell
# Navigate to the project
cd C:\Users\YourUsername\Documents\SmartPGP

# Run the self-test script
cd outlook_helper\windows\SmartPGP.OutlookHelper\tests
.\selftest.ps1
```

**Expected results**:
```
✓ Card is present
✓ Found encryption key on card
✓ Encryption succeeded
✓ Decryption succeeded
✓ Helper produces PGP-compatible output

All tests passed!
```

**If tests fail**: See [Troubleshooting](#troubleshooting) section.

### Step 1.9: Setup Outlook Add-in

```powershell
# Navigate to add-in directory
cd ..\..\..\..\outlook_addin

# Install Node.js dependencies
npm install

# Start the add-in HTTPS server
npm start
```

**Expected output**:
```
SmartPGP Outlook Add-in Server
Listening on https://localhost:3000

Available resources:
  https://localhost:3000/manifest.xml - Add-in manifest
  https://localhost:3000/taskpane.html - Task pane UI
  https://localhost:3000/functions.html - Function commands

Keep this server running while testing the add-in.
```

**Keep this window open too!** You now have 2 terminals running:
1. Helper service (port 5555)
2. Add-in server (port 3000)

### Step 1.10: Generate Keypair on Card (Windows)

**If your card doesn't have keys yet:**

```powershell
# Open a NEW PowerShell window
cd C:\Users\YourUsername\Documents\SmartPGP\outlook_helper\windows\SmartPGP.OutlookHelper

# Generate keypair (this takes 30-120 seconds)
curl -X POST https://127.0.0.1:5555/generate-keypair `
  -H "Content-Type: application/json" `
  -d '{"adminPin":"12345678"}'
```

**Note**: Default admin PIN is `12345678`. Change if you've modified it.

**Expected output** (after 30-120 seconds):
```json
{
  "success": true,
  "message": "Keypair generated successfully on card",
  "keySlot": "Encryption"
}
```

**Windows Setup Complete!** ✅

---

## Setup Phase 2: macOS Testing

### Step 2.1: Clone the Repository

```bash
# Open Terminal (Cmd + Space, type "Terminal")

# Navigate to your desired location
cd ~/Documents

# Clone the repository
git clone https://github.com/yourusername/SmartPGP.git

# Navigate to the project
cd SmartPGP

# Switch to the outlookintegration branch
git checkout outlookintegration
```

### Step 2.2: Install Homebrew (if not installed)

```bash
# Check if Homebrew is installed
which brew

# If not found, install Homebrew:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Follow on-screen instructions to add Homebrew to PATH
```

### Step 2.3: Install Dependencies

```bash
# Install GnuPG
brew install gnupg

# Install GPGME
brew install gpgme

# Install Node.js (if not already installed)
brew install node

# Verify installations
gpg --version
gpgme-config --version
node --version
swift --version
```

### Step 2.4: Configure Card Reader (macOS)

1. Connect your smart card reader to USB
2. Insert AEPGP SmartPGP card
3. Open Terminal and run:
   ```bash
   gpg --card-status
   ```
4. **First time setup**: macOS should automatically detect the reader
5. Expected output should show:
   - Reader name
   - Application ID (starts with D2760001...)
   - Version information
   - Key slots (may be empty if new card)

**Troubleshooting**: If card is not detected:
- Check System Preferences → Security & Privacy → Smart Card settings
- Try: `killall scdaemon` then `gpg --card-status` again
- Some readers may need drivers from the manufacturer

### Step 2.5: Build macOS Helper

```bash
# Navigate to macOS helper directory
cd outlook_helper/macos/SmartPGP.OutlookHelper

# Build the project (this will download dependencies)
swift build --configuration release

# This takes 2-5 minutes the first time
```

**Expected output**:
```
Fetching https://github.com/vapor/vapor.git
Fetching https://github.com/apple/swift-nio-ssl.git
...
Build complete! (XX.XXs)
```

**If build fails**:
- Ensure Xcode Command Line Tools are installed: `xcode-select --install`
- Verify Swift version: `swift --version` (should be 5.9+)
- Check that GPGME is installed: `brew list gpgme`

### Step 2.6: Generate Certificate (macOS)

```bash
# Still in outlook_helper/macos/SmartPGP.OutlookHelper directory

# Create certs directory
mkdir -p certs

# Generate self-signed certificate using OpenSSL
openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout certs/localhost-key.pem \
  -out certs/localhost-cert.pem \
  -days 365 \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1"

# Combine cert and key into single PEM file
cat certs/localhost-cert.pem certs/localhost-key.pem > certs/localhost.pem

echo "Certificate created at certs/localhost.pem"
```

#### Install Certificate to Keychain

```bash
# Add certificate to Keychain
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain \
  certs/localhost-cert.pem

echo "Certificate installed to System Keychain"
```

**Verify**: Open **Keychain Access** app → System → Certificates → Look for "localhost"

#### Generate Add-in Certificate

```bash
# Navigate to add-in directory
cd ../../../outlook_addin

# Create certs directory
mkdir -p certs

# Generate certificate
openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout certs/addin-localhost-key.pem \
  -out certs/addin-localhost-cert.pem \
  -days 365 \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1"

# Combine for server use
cat certs/addin-localhost-cert.pem certs/addin-localhost-key.pem > certs/addin-localhost.pem

# Install to Keychain
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain \
  certs/addin-localhost-cert.pem

echo "Add-in certificate installed"
```

### Step 2.7: Configure macOS Helper

```bash
# Navigate to macOS helper directory
cd ../outlook_helper/macos/SmartPGP.OutlookHelper

# Create .env file from example
cp .env.example .env

# Edit configuration
nano .env
```

**Verify the configuration** (should be similar to this):
```bash
SMARTPGP_PORT=5555
SMARTPGP_ALLOWED_ORIGINS=https://localhost,https://outlook.office.com,https://outlook.live.com
SMARTPGP_CERT_PATH=certs/localhost.pem
# SMARTPGP_CERT_PASSWORD=  # Not needed for PEM files
# SMARTPGP_SIGNER_ID=  # Optional, leave commented for encrypt-only
```

Press `Ctrl+X`, then `Y`, then `Enter` to save.

### Step 2.8: Start macOS Helper

```bash
# In outlook_helper/macos/SmartPGP.OutlookHelper directory

# Run the helper service
.build/release/SmartPGP.OutlookHelper
```

**Alternative if you didn't build in release mode**:
```bash
swift run SmartPGP.OutlookHelper
```

**Expected output**:
```
SmartPGP Outlook Helper for macOS
Listening on https://127.0.0.1:5555
Allowed origins: https://localhost, https://outlook.office.com, https://outlook.live.com
Signer ID: (none)

Available endpoints:
  POST /encrypt       - Encrypt plaintext for recipients
  POST /decrypt       - Decrypt PGP message
  POST /generate-keypair - Generate new keypair on card
  POST /change-pin    - Change card PIN
  POST /delete-keypair - Delete all keys (factory reset)
  GET  /card-status   - Get card status
  GET  /healthz       - Health check
```

**Keep this Terminal window open!**

### Step 2.9: Test macOS Helper (Self-Test)

**Open a NEW Terminal window** (Cmd+N) while keeping the helper running.

```bash
# Navigate to the project
cd ~/Documents/SmartPGP

# Run the self-test script
cd outlook_helper/macos/SmartPGP.OutlookHelper/tests
./selftest.sh
```

**Expected results** (with colors):
```
✓ Helper is running
✓ Card is present
✓ Encryption succeeded
✓ Decryption succeeded
✓ GPG CLI can decrypt helper output

All tests passed!
```

**If tests fail**: See [Troubleshooting](#troubleshooting) section.

### Step 2.10: Setup Outlook Add-in

```bash
# Navigate to add-in directory
cd ../../../../outlook_addin

# Install Node.js dependencies
npm install

# Start the add-in HTTPS server
# Note: You may need to create a server.js file or use the one provided
npm start
```

**Expected output**:
```
SmartPGP Outlook Add-in Server
Listening on https://localhost:3000
...
```

**Keep this window open too!** You now have 2 terminals running:
1. Helper service (port 5555)
2. Add-in server (port 3000)

### Step 2.11: Generate Keypair on Card (macOS)

**If your card doesn't have keys yet:**

```bash
# Open a NEW Terminal window
cd ~/Documents/SmartPGP/outlook_helper/macos/SmartPGP.OutlookHelper

# Generate keypair (this takes 30-120 seconds)
curl -X POST https://127.0.0.1:5555/generate-keypair \
  -H "Content-Type: application/json" \
  -d '{"adminPin":"12345678"}' \
  -k  # -k flag ignores certificate warnings
```

**Expected output** (after 30-120 seconds):
```json
{
  "success": true,
  "message": "Keypair generated successfully on card",
  "keySlot": "Encryption"
}
```

**macOS Setup Complete!** ✅

---

## Testing Outlook Desktop (Windows)

### Prerequisites
- ✅ Windows helper is running (port 5555)
- ✅ Add-in server is running (port 3000)
- ✅ SmartPGP card is inserted with encryption key
- ✅ Outlook Desktop is installed

### Step 1: Sideload the Add-in Manifest

1. **Open Outlook Desktop** on Windows
2. Click **File** → **Manage Add-ins**
   - (Or click the **Get Add-ins** button in the ribbon)
3. In the web browser that opens, click **My add-ins** (left sidebar)
4. Scroll down to **Custom add-ins** section
5. Click **+ Add a custom add-in** → **Add from file...**
6. Browse to: `C:\Users\YourUsername\Documents\SmartPGP\outlook_addin\manifest\manifest.xml`
7. Click **Open**
8. Click **Install** in the warning dialog
9. Close the browser window
10. **Restart Outlook Desktop**

**Verification**:
- After restart, you should see a **SmartPGP** section in the ribbon when composing or reading emails

### Step 2: Test Encryption (Compose Email)

1. Click **New Email** in Outlook
2. In the compose window:
   - **To**: Enter `recipient@example.com` (or any valid email)
   - **Subject**: `Test Encrypted Email`
   - **Body**: Type some test message like:
     ```
     This is a test of SmartPGP encryption via Outlook.
     Secret message: The password is "blue42"
     ```

3. Look for the **SmartPGP** section in the ribbon (may be under "Message" tab)
4. Click **Encrypt & Send** button

**What happens**:
- The add-in contacts the helper service (port 5555)
- Helper retrieves your public key from the card
- Helper encrypts the message body
- **You may see a PIN entry dialog** - enter your user PIN (default: `123456`)
- Body is replaced with PGP encrypted text (starts with `-----BEGIN PGP MESSAGE-----`)
- Custom header `smartpgp-encrypted: 1` is added
- Email is sent

**Expected result**:
```
-----BEGIN PGP MESSAGE-----

hQEMA+abc123...encrypted content...xyz789==
=abcd
-----END PGP MESSAGE-----
```

**Send the email!** (It will actually send, so use a test email address you control)

### Step 3: Test Decryption (Read Email)

**Option A: Receive encrypted email from yourself**
1. Wait to receive the test email you sent
2. Open the encrypted email
3. You'll see the encrypted PGP block
4. Look for **SmartPGP** section in the ribbon
5. Click **Decrypt** button

**Option B: Manually create a test encrypted message**
1. Click **New Email**
2. Send yourself an email with this encrypted content in the body:
   ```
   -----BEGIN PGP MESSAGE-----
   (use the output from your encryption test)
   -----END PGP MESSAGE-----
   ```
3. Open that email
4. Click **Decrypt** button

**What happens**:
- A task pane opens on the right side
- The add-in sends the PGP message to the helper
- Helper asks the card to decrypt using the private key
- **You may see a PIN entry dialog** - enter your user PIN (default: `123456`)
- Decrypted plaintext appears in the task pane

**Expected result in task pane**:
```
✓ Decrypted successfully:

This is a test of SmartPGP encryption via Outlook.
Secret message: The password is "blue42"
```

### Step 4: Test OnMessageSend Auto-Encryption (Optional)

The add-in can auto-encrypt when you click the regular "Send" button:

1. Click **New Email**
2. Compose a message (recipient, subject, body)
3. Click the regular **Send** button (NOT "Encrypt & Send")
4. **Currently**: The OnMessageSend handler runs but may need additional configuration
5. Check the **Sent** folder to see if the message was encrypted

**Note**: Auto-encryption may require additional configuration. The manual "Encrypt & Send" button is the primary test.

**Windows Desktop Testing Complete!** ✅

---

## Testing Outlook Desktop (macOS)

### Prerequisites
- ✅ macOS helper is running (port 5555)
- ✅ Add-in server is running (port 3000)
- ✅ SmartPGP card is inserted with encryption key
- ✅ Outlook Desktop is installed (Microsoft 365 for Mac)

### Step 1: Sideload the Add-in Manifest

1. **Open Outlook Desktop** on macOS
2. Click **Outlook** menu → **Preferences** → **Add-ins**
   - (Or Tools → Add-ins in some versions)
3. In the **Add-ins** window, click the **gear icon** (⚙️) in the bottom left
4. Click **Custom Add-ins**
5. Click **Add from file...**
6. Browse to: `~/Documents/SmartPGP/outlook_addin/manifest/manifest.xml`
7. Click **Open**
8. Click **Install** in the warning dialog
9. **Restart Outlook Desktop**

**Alternative Method** (if above doesn't work):
```bash
# Copy manifest to Outlook add-ins folder
mkdir -p ~/Library/Containers/com.microsoft.Outlook/Data/Library/Application\ Support/Microsoft/Office/16.0/Wef/

cp ~/Documents/SmartPGP/outlook_addin/manifest/manifest.xml \
   ~/Library/Containers/com.microsoft.Outlook/Data/Library/Application\ Support/Microsoft/Office/16.0/Wef/SmartPGP.xml
```

**Verification**:
- After restart, you should see a **SmartPGP** section when composing or reading emails

### Step 2: Test Encryption (Compose Email)

Same steps as Windows:

1. Click **New Message** in Outlook
2. In the compose window:
   - **To**: Enter `recipient@example.com` (or any valid email)
   - **Subject**: `Test Encrypted Email from Mac`
   - **Body**: Type test message
3. Look for **SmartPGP** button/section in the ribbon
4. Click **Encrypt & Send**

**PIN Entry**: macOS may use a GUI dialog or terminal-based entry depending on your `pinentry` configuration.

**Expected result**: Body is replaced with PGP encrypted text.

### Step 3: Test Decryption (Read Email)

Same steps as Windows:

1. Open an email with PGP encrypted content
2. Click **Decrypt** button in SmartPGP section
3. Task pane opens showing decrypted content

**macOS Desktop Testing Complete!** ✅

---

## Testing Outlook Web with Browser Extension

### ✅ Solution: Browser Extension

The **Browser Extension** solves the Outlook Web limitation by using Chrome/Firefox extension permissions to bypass browser CORS restrictions. Unlike the Office Add-in (which fails in Outlook Web), the browser extension **actually works** for encryption and decryption.

**How It Works**:
- Extension injects a **floating SmartPGP widget** in the bottom-right corner of Outlook Web
- Widget has input/output areas, recipients field, and encrypt/decrypt buttons
- Extension permissions allow calling `https://127.0.0.1:5555` (Office Add-in cannot do this)
- User manually **copies/pastes** between Outlook and widget (trade-off for functionality)

### Prerequisites
- ✅ Helper service is running (Windows or macOS, port 5555)
- ✅ SmartPGP card is inserted with encryption key
- ✅ Microsoft 365 account (outlook.office.com or outlook.live.com)
- ✅ Chrome, Firefox, or Edge browser

### Step 1: Install Browser Extension

**Chrome or Edge**:

1. Open `chrome://extensions` (Chrome) or `edge://extensions` (Edge)
2. Enable **"Developer mode"** toggle in the top-right corner
3. Click **"Load unpacked"** button
4. Navigate to and select: `SmartPGP/browser_extension/` folder
5. Extension should appear in the list with a SmartPGP icon
6. **Pin the extension**: Click the puzzle icon in browser toolbar → Pin SmartPGP

**Firefox**:

1. Open `about:debugging#/runtime/this-firefox`
2. Click **"Load Temporary Add-on..."** button
3. Navigate to `SmartPGP/browser_extension/`
4. Select `manifest.firefox.json` file
5. Extension loads temporarily (will be removed when Firefox restarts)

**Verify Installation**:
- Extension icon should appear in browser toolbar
- Click icon to see configuration popup

### Step 2: Configure Helper URL

1. **Click the SmartPGP extension icon** in browser toolbar
2. A small popup appears with a "Helper URL" field
3. **Default value should be**: `https://127.0.0.1:5555`
   - If you're using a different port, change it here
4. Click **"Save"** button
5. You should see: "Settings saved!" message

**Note**: This URL is stored in `chrome.storage.sync` and syncs across devices.

### Step 3: Trust Helper Certificate (if not already done)

The browser must trust your helper's self-signed certificate:

**Windows**:
```powershell
# Already done in Setup Phase 1 - certificate installed to Windows Certificate Store
# Chrome/Edge use Windows certificate store automatically

# Firefox uses its own certificate store:
# Settings → Privacy & Security → Certificates → View Certificates
# Authorities → Import → Select outlook_helper/windows/SmartPGP.OutlookHelper/certs/localhost.pfx
```

**macOS**:
```bash
# Already done in Setup Phase 2 - certificate added to System Keychain
# Chrome/Edge use macOS Keychain automatically

# Firefox uses its own certificate store:
# Settings → Privacy & Security → Certificates → View Certificates
# Authorities → Import → Select outlook_helper/macos/SmartPGP.OutlookHelper/certs/localhost-cert.pem
```

### Step 4: Navigate to Outlook Web

1. Go to https://outlook.office.com (or https://outlook.live.com)
2. Log in with your Microsoft account
3. **A floating widget should automatically appear** in the bottom-right corner
   - Dark theme with "SmartPGP Bridge" header
   - Close button (X) in top-right of widget
   - Input/output textareas and encrypt/decrypt buttons

**If widget doesn't appear**:
- Refresh the page (Ctrl+R or Cmd+R)
- Check browser console (F12 → Console) for errors
- Verify extension is installed and enabled
- Try clicking extension icon to verify helper URL is configured

### Step 5: Test Encryption (Scenario 3 or 4)

#### Compose Email in Outlook Web

1. Click **"New message"** in Outlook Web
2. Fill in:
   - **To**: `recipient@example.com` (use an email you control for testing)
   - **Subject**: `Test Encrypted Email via Browser Extension`
   - **Body**: Type your test message:
     ```
     This is a test of SmartPGP encryption via Browser Extension.
     Secret message: The meeting is at 3PM.
     ```

#### Use Widget to Encrypt

3. **Select and copy** your message text from the Outlook compose field (Ctrl+C / Cmd+C)
4. **Click inside the SmartPGP widget's input textarea** (top textarea)
5. **Paste** the text (Ctrl+V / Cmd+V)
6. **Enter recipient email** in the "Recipients" field:
   - Type: `recipient@example.com`
   - For multiple recipients: `alice@example.com,bob@example.com` (comma-separated)
7. **Click "Encrypt" button** (green button)

**What happens**:
- Widget shows status: "Encrypting..."
- Extension calls: `POST https://127.0.0.1:5555/encrypt`
- Helper retrieves public key from your SmartPGP card
- **You may see PIN entry dialog** - enter user PIN (default: `123456`)
- Helper encrypts message using card's public key
- Widget displays encrypted output in bottom textarea

**Expected output** (in widget's output area):
```
-----BEGIN PGP MESSAGE-----

hQEMA+abc123xyz...long encrypted string...789==
=ABCD
-----END PGP MESSAGE-----
```

#### Copy Encrypted Text Back to Outlook

8. **Select all text** in the widget's output area
9. **Copy** the encrypted text (Ctrl+A then Ctrl+C / Cmd+A then Cmd+C)
10. Go back to Outlook compose field
11. **Select all original text** in the body and **delete** it
12. **Paste** the encrypted text (Ctrl+V / Cmd+V)
13. **Click "Send"** button in Outlook

**Result**: Email is sent with PGP-encrypted body! ✅

### Step 6: Test Decryption (Scenario 3 or 4)

#### Receive Encrypted Email

1. **Wait to receive** the encrypted email you sent (or send yourself one from Desktop Outlook)
2. **Open the encrypted email** in Outlook Web
3. You'll see the PGP-encrypted block:
   ```
   -----BEGIN PGP MESSAGE-----
   ...encrypted content...
   -----END PGP MESSAGE-----
   ```

#### Use Widget to Decrypt

4. **Select and copy** the entire PGP block from the email (Ctrl+A in email body, then Ctrl+C)
5. **Click inside the SmartPGP widget's input textarea**
6. **Paste** the encrypted text (Ctrl+V / Cmd+V)
7. **Click "Decrypt" button** (blue button)

**What happens**:
- Widget shows status: "Decrypting..."
- Extension calls: `POST https://127.0.0.1:5555/decrypt`
- Helper sends encrypted data to SmartPGP card via GPGME
- **PIN entry dialog appears** - enter user PIN (default: `123456`)
- Card performs RSA decryption using private key (never leaves card!)
- Helper returns plaintext
- Widget displays decrypted message in output area

**Expected output** (in widget's output area):
```
This is a test of SmartPGP encryption via Browser Extension.
Secret message: The meeting is at 3PM.
```

**Success!** You've decrypted an email using hardware-backed cryptography. ✅

### Step 7: Close Widget (Optional)

- Click the **X button** in the widget's header to close it
- Widget can be re-opened by refreshing the page
- Widget state is not persistent (resets on page load)

### Verification Checklist

For Browser Extension testing, verify:
- [ ] Extension installs without errors (Chrome/Edge/Firefox)
- [ ] Helper URL is configurable via popup
- [ ] Widget appears automatically on Outlook Web
- [ ] Widget UI is responsive (input/output areas, buttons)
- [ ] Encryption works (widget → helper → card → encrypted output)
- [ ] Decryption works (encrypted input → helper → card → plaintext)
- [ ] PIN entry dialog appears during crypto operations
- [ ] Encrypted emails can be sent via Outlook Web
- [ ] Received encrypted emails can be decrypted in widget

**Outlook Web Testing Complete!** ✅ (Full encryption/decryption works via Browser Extension)

---

## Troubleshooting

### General Issues

#### "Certificate not trusted" errors

**Windows**:
```powershell
# Re-import certificates with admin privileges
# Run PowerShell as Administrator
$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2
$cert.Import("path\to\cert.pfx", "change-me", "UserKeySet")
$store = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root", "CurrentUser")
$store.Open("ReadWrite")
$store.Add($cert)
$store.Close()
```

**macOS**:
```bash
# Re-install certificate with trust
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain \
  path/to/cert.pem
```

**Browsers**: Some browsers (Firefox) use their own certificate store:
- Firefox: Settings → Privacy & Security → Certificates → View Certificates → Authorities → Import

#### "Port already in use" (5555 or 3000)

**Windows**:
```powershell
# Find process using port 5555
netstat -ano | findstr :5555

# Kill process by PID (replace 1234 with actual PID)
taskkill /PID 1234 /F
```

**macOS**:
```bash
# Find process using port 5555
lsof -i :5555

# Kill process by PID
kill -9 <PID>
```

#### Card not detected

**Both platforms**:
```bash
# Restart GPG daemon
gpgconf --kill scdaemon
gpg --card-status

# Try different reader mode
echo "reader-port \"USB READER NAME\"" >> ~/.gnupg/scdaemon.conf
gpgconf --reload scdaemon
```

**Windows specific**:
- Check Device Manager → Smart Card Readers
- Try a different USB port
- Restart the "Smart Card" service:
  ```powershell
  net stop SCardSvr
  net start SCardSvr
  ```

### Helper Service Issues

#### "GPGME context failed" or "No usable secret key"

**Check that GPG can see the card**:
```bash
gpg --card-status
gpg --list-secret-keys
```

**If no secret keys shown**:
```bash
# Import key stubs from card
gpg --card-edit
> fetch
> quit

gpg --list-secret-keys  # Should now show keys with '>' marker
```

#### Windows Helper: "GpgmeSharp not found"

```powershell
# Reinstall NuGet package
cd outlook_helper\windows\SmartPGP.OutlookHelper
dotnet restore --force
dotnet build
```

#### macOS Helper: "Library not loaded: libgpgme"

```bash
# Verify GPGME installation
brew list gpgme
gpgme-config --version

# Reinstall if needed
brew uninstall gpgme
brew install gpgme

# Rebuild helper
swift build --configuration release
```

#### "Encryption failed: No public key found"

**This means the card doesn't have an encryption key**. Generate one:

**Windows**:
```powershell
curl -X POST https://127.0.0.1:5555/generate-keypair `
  -H "Content-Type: application/json" `
  -d '{"adminPin":"12345678"}'
```

**macOS**:
```bash
curl -X POST https://127.0.0.1:5555/generate-keypair \
  -H "Content-Type: application/json" \
  -d '{"adminPin":"12345678"}' -k
```

Wait 30-120 seconds for key generation to complete.

### Outlook Add-in Issues

#### Add-in doesn't appear after sideloading

**Windows Outlook**:
1. Close Outlook completely (check Task Manager - no OUTLOOK.EXE)
2. Delete cache: `%LOCALAPPDATA%\Microsoft\Outlook\16.0\Wef\`
3. Restart Outlook
4. Re-sideload the add-in

**macOS Outlook**:
```bash
# Clear add-in cache
rm -rf ~/Library/Containers/com.microsoft.Outlook/Data/Library/Caches/com.microsoft.Outlook/
# Restart Outlook
```

#### "Encrypt & Send" button does nothing

**Check browser console** (if using Outlook Web):
1. Press F12 to open developer tools
2. Go to **Console** tab
3. Look for JavaScript errors
4. Common issues:
   - `Failed to fetch` - Helper not running or certificate issue
   - `Office is not defined` - Office.js not loaded
   - CORS errors - Check helper configuration

**Check helper is running**:
```bash
# Should return {"status":"healthy"}
curl https://127.0.0.1:5555/healthz -k
```

#### Task pane is blank when clicking "Decrypt"

**Verify taskpane.html is accessible**:
- Navigate to: `https://localhost:3000/taskpane.html` in browser
- You should see the decryption UI

**If not accessible**:
- Check that `npm start` is running
- Check for errors in the terminal where you ran `npm start`

### Build Errors

#### Windows: ".NET SDK not found"

Download and install .NET 8 SDK: https://dotnet.microsoft.com/download/dotnet/8.0

#### macOS: "No such module 'NIOSSL'"

**This should NOT happen** if you're using the latest code, but if it does:

```bash
# Edit Package.swift
nano Package.swift

# Add to dependencies array:
.package(url: "https://github.com/apple/swift-nio-ssl.git", from: "2.0.0"),

# Add to target dependencies:
.product(name: "NIOSSL", package: "swift-nio-ssl"),

# Save and rebuild
swift build --configuration release
```

#### macOS: "gpgme.h not found"

```bash
# Install GPGME
brew install gpgme

# Verify installation
gpgme-config --cflags
gpgme-config --libs

# If still failing, add explicit paths to Package.swift
```

---

## FAQ

### Q1: Do I need to keep the terminal windows open?

**Yes**, while testing:
- Helper service terminal must stay open (port 5555)
- Add-in server terminal must stay open (port 3000)
- Closing them will stop the services

For production use, you would set them up as system services (Windows Service / macOS LaunchAgent).

### Q2: Can I use this with a real email address?

**Yes!** The encryption is real. However:
- The **recipient must also have SmartPGP** (or compatible PGP software) to decrypt
- Test with email addresses you control first
- For demos, use a test email account

### Q3: Why does key generation take so long?

**Hardware limitation**: The SmartPGP card generates the keypair internally for security. RSA-2048 key generation on a smart card CPU takes 30-120 seconds. This is normal and cannot be accelerated.

### Q4: What's the default PIN?

- **User PIN** (for signing/decryption): `123456`
- **Admin PIN** (for card management): `12345678`

**IMPORTANT**: Change these PINs for production use!

```bash
# Change user PIN
curl -X POST https://127.0.0.1:5555/change-pin \
  -H "Content-Type: application/json" \
  -d '{"currentPin":"123456","newPin":"your-new-pin"}' -k
```

### Q5: Will Outlook Web ever work fully?

**Not with the current localhost architecture**. Possible future solutions:
1. **Cloud relay service** - Deploy a cloud service that tunnels to your local helper
2. **Browser extension** - Replace Office Add-in with a Chrome/Firefox extension
3. **Desktop companion app** - Manual copy/paste workflow

All require additional development work.

### Q6: Can I distribute this to my team?

**For testing**: Yes, each person must:
- Run their own helper service
- Have their own SmartPGP card
- Generate their own certificates
- Sideload the add-in

**For production deployment**:
- Package the helpers as installable services
- Sign code with proper certificates
- Submit add-in to Microsoft AppSource (for automatic distribution)
- Set up centralized certificate authority

### Q7: Is this secure?

**Yes**, with proper usage:
- Private keys **never leave the smart card**
- All crypto operations happen on the card
- HTTPS protects communication between add-in and helper
- Helper only accepts requests from allowed origins (CORS)

**Security notes**:
- Use strong PINs (not defaults)
- Use production certificates (not self-signed)
- Keep card physically secure
- Review code before deploying to production

### Q8: What if I get "PIN blocked" errors?

**The card blocks after 3 failed PIN attempts**.

**To unblock**:
1. You need the **admin PIN** (default: `12345678`)
2. Use GPG to unblock:
   ```bash
   gpg --card-edit
   > admin
   > passwd
   > 2  # Unblock PIN
   # Enter admin PIN
   # Set new user PIN
   > quit
   ```

### Q9: Can I use this with Gmail/other email clients?

**Not directly**. This integration is specifically for **Microsoft Outlook** (Desktop and Web).

For other clients:
- Use GPG directly via command line
- Use other PGP integrations (like Mailvelope for Gmail)
- The helper service API could theoretically be adapted for other clients

### Q10: How do I stop everything when done testing?

```bash
# Stop helper service: Press Ctrl+C in the helper terminal
# Stop add-in server: Press Ctrl+C in the add-in terminal

# Remove add-in from Outlook Desktop:
# Outlook → File → Manage Add-ins → Remove SmartPGP

# Remove add-in from Outlook Web:
# Settings → Manage Add-ins → Remove SmartPGP
```

---

## Next Steps

After completing all tests:

### ✅ Success Checklist

**Helper Services**:
- [ ] Windows helper builds and runs without errors
- [ ] macOS helper builds and runs without errors
- [ ] Self-tests pass on both platforms (`/api/test` endpoint returns success)

**Scenario 1: Windows Desktop (Office Add-in)**:
- [ ] Outlook Desktop (Windows) - Encrypt works via ribbon button
- [ ] Outlook Desktop (Windows) - Decrypt works via ribbon button

**Scenario 2: macOS Desktop (Office Add-in)**:
- [ ] Outlook Desktop (macOS) - Encrypt works via ribbon button
- [ ] Outlook Desktop (macOS) - Decrypt works via ribbon button

**Scenario 3: Windows Web (Browser Extension)**:
- [ ] Browser extension installs successfully (Chrome/Edge/Firefox)
- [ ] SmartPGP widget appears in Outlook Web
- [ ] Outlook Web - Encrypt works via widget
- [ ] Outlook Web - Decrypt works via widget

**Scenario 4: macOS Web (Browser Extension)**:
- [ ] Browser extension installs successfully (Chrome/Edge/Firefox/Safari)
- [ ] SmartPGP widget appears in Outlook Web
- [ ] Outlook Web - Encrypt works via widget
- [ ] Outlook Web - Decrypt works via widget

**Documentation**:
- [ ] All setup instructions are clear and helpful
- [ ] Troubleshooting section addresses encountered issues

### 📝 Feedback

If you found issues or have suggestions:
1. Document what failed and error messages
2. Note your platform (Windows/macOS version, Outlook version)
3. Share browser console errors (if applicable)
4. Create a GitHub issue or contact the team

### 🚀 Production Deployment

For production use, additional steps needed:
1. **Certificate Management**:
   - Obtain proper SSL certificates (not self-signed)
   - Set up certificate rotation

2. **Service Deployment**:
   - Package helpers as Windows Service / macOS LaunchAgent
   - Create installers (.msi for Windows, .pkg for macOS)
   - Code signing for both platforms

3. **Add-in Publishing**:
   - Update manifest with production URLs
   - Submit to Microsoft AppSource
   - Set up centralized deployment for organizations

4. **Security Hardening**:
   - Change all default PINs
   - Review and harden CORS policies
   - Implement rate limiting
   - Add audit logging

5. **Documentation**:
   - User guide for end users
   - IT admin deployment guide
   - Security policy documentation

---

## Support Resources

- **Main README**: `../README.md`
- **Windows Helper README**: `outlook_helper/windows/README.md`
- **macOS Helper README**: `outlook_helper/macos/README.md`
- **Implementation Summary**: `outlook_helper/macos/IMPLEMENTATION_SUMMARY.md`
- **SmartPGP Specification**: https://gnupg.org/ftp/specs/OpenPGP-smart-card-application-3.4.pdf

---

**Good luck with your testing!** 🎉

If you've made it this far, you now know how to test a complete Outlook integration with SmartPGP cards. This is enterprise-grade encryption at your fingertips!
