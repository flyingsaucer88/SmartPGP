# SmartPGP Outlook Helper for macOS

A localhost HTTPS server that provides PGP encryption, decryption, and card management operations for SmartPGP cards on macOS. This helper enables Outlook add-ins and other applications to interact with SmartPGP hardware tokens.

## Features

- **Encryption/Decryption**: Standard OpenPGP encryption and decryption using GPGME
- **Card Management**: Generate keypairs, change PIN, delete keys (factory reset)
- **Card Status**: Query card information and key status
- **Security**: Localhost-only binding, CORS protection, hardware-backed private keys
- **Compatibility**: Works with standard OpenPGP cards and SmartPGP tokens

## Prerequisites

### Required

1. **macOS 12.0 or later**
2. **GnuPG with smartcard support**:
   ```bash
   brew install gnupg
   ```

3. **GPGME library**:
   ```bash
   brew install gpgme
   ```

4. **Swift 5.9 or later** (included with Xcode Command Line Tools):
   ```bash
   xcode-select --install
   ```

5. **SmartPGP card** with proper drivers installed

### Optional

- **Vapor CLI** (for development):
  ```bash
  brew install vapor
  ```

## Installation

### 1. Clone and Build

```bash
cd outlook_helper/macos/SmartPGP.OutlookHelper
swift build -c release
```

The compiled binary will be at `.build/release/SmartPGP.OutlookHelper`.

### 2. Verify Card Setup

Ensure your SmartPGP card is recognized:

```bash
gpg --card-status
```

You should see card information including serial number and key slots.

### 3. Configure (Optional)

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` to customize:
- `SMARTPGP_PORT`: Server port (default: 5555)
- `SMARTPGP_ALLOWED_ORIGIN`: CORS origin (default: https://localhost)
- `SMARTPGP_SIGNER_ID`: Optional signer key ID for encryption+signing

## Usage

### Running the Helper

```bash
# Run directly
./.build/release/SmartPGP.OutlookHelper

# Or with custom port
SMARTPGP_PORT=5556 ./.build/release/SmartPGP.OutlookHelper
```

The server will start on `https://127.0.0.1:5555` by default.

### Running Self-Tests

```bash
cd tests
./selftest.sh

# Or with custom recipient
RECIPIENT=your@email.com ./selftest.sh
```

## API Endpoints

### Health Check
```
GET /healthz
Response: "ok"
```

### Encrypt
```
POST /encrypt
Content-Type: application/json

Request:
{
  "body": "plaintext message",
  "recipients": ["recipient@example.com"]
}

Response:
{
  "armored": "-----BEGIN PGP MESSAGE-----\n..."
}
```

### Decrypt
```
POST /decrypt
Content-Type: application/json

Request:
{
  "body": "-----BEGIN PGP MESSAGE-----\n..."
}

Response:
{
  "plaintext": "decrypted message"
}
```

### Generate Keypair
```
POST /generate-keypair
Content-Type: application/json

Request:
{
  "keySize": 2048,           // Optional, default: 2048
  "adminPin": "12345678"      // Optional, default: 12345678
}

Response:
{
  "success": true,
  "message": "RSA-2048 keypair generated successfully on card",
  "keyId": "ABC123..."
}
```

**Note**: This operation takes 30-120 seconds and will overwrite existing keys!

### Change PIN
```
POST /change-pin
Content-Type: application/json

Request:
{
  "currentPin": "123456",
  "newPin": "newpin123"
}

Response:
{
  "success": true,
  "message": "PIN changed successfully"
}
```

**Requirements**: PIN must be 6-127 characters.

### Delete Keypair (Factory Reset)
```
POST /delete-keypair
Content-Type: application/json

Request:
{
  "adminPin": "12345678"      // Optional, default: 12345678
}

Response:
{
  "success": true,
  "message": "Card reset to factory defaults. Default PIN: 123456, Admin PIN: 12345678"
}
```

**Warning**: This operation is irreversible and will delete all keys!

### Card Status
```
GET /card-status

Response:
{
  "cardPresent": true,
  "hasSigningKey": true,
  "hasEncryptionKey": true,
  "hasAuthenticationKey": false,
  "serialNumber": "D276000124010304...",
  "rawStatus": "... full gpg --card-status output ..."
}
```

## Development

### Project Structure

```
SmartPGP.OutlookHelper/
├── Package.swift           # Swift package configuration
├── Sources/
│   ├── main.swift         # Main application and routes
│   ├── GPGME.swift        # GPGME C API wrapper
│   └── CardService.swift  # Card management operations
├── tests/
│   └── selftest.sh        # Self-test script
├── .env.example           # Configuration template
└── README.md              # This file
```

### Building for Development

```bash
swift build
swift run
```

### Running Tests

```bash
# Run self-tests
cd tests && ./selftest.sh

# Or with custom configuration
HELPER_URL=https://127.0.0.1:5556 RECIPIENT=test@example.com ./selftest.sh
```

## Troubleshooting

### "Card not found" Error

1. Check card is inserted:
   ```bash
   gpg --card-status
   ```

2. Restart GPG agent:
   ```bash
   gpgconf --kill gpg-agent
   gpgconf --kill scdaemon
   ```

3. Check USB connection and card reader

### "GPGME initialization failed"

1. Verify GPGME is installed:
   ```bash
   brew list gpgme
   ```

2. Check library paths:
   ```bash
   ls -l /opt/homebrew/lib/libgpgme*
   ls -l /usr/local/lib/libgpgme*
   ```

3. Rebuild the project:
   ```bash
   swift build -c release
   ```

### "Permission denied" on Certificate

If using a custom TLS certificate:

```bash
chmod 600 certs/localhost.p12
```

### GPG Agent Issues

Kill and restart GPG agent:

```bash
gpgconf --kill gpg-agent
gpgconf --kill scdaemon
gpg-agent --daemon
```

## Security Considerations

1. **Localhost Only**: The helper binds to 127.0.0.1 and is not accessible from network
2. **CORS Protection**: Only configured origins can access the API
3. **Hardware-Backed Keys**: Private keys never leave the SmartPGP card
4. **PIN Entry**: PIN prompts are handled by GPG agent/pinentry
5. **Standard OpenPGP**: Uses standard armored messages for interoperability

## Deployment

### As a LaunchAgent (Auto-Start)

Create a launchd plist file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.smartpgp.outlookhelper</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/SmartPGP.OutlookHelper</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/smartpgp-helper.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/smartpgp-helper-error.log</string>
</dict>
</plist>
```

Install and start:

```bash
cp com.smartpgp.outlookhelper.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.smartpgp.outlookhelper.plist
```

## Comparison with Windows Version

| Feature | Windows (.NET) | macOS (Swift) |
|---------|---------------|---------------|
| Encryption | ✅ GPGME | ✅ GPGME |
| Decryption | ✅ GPGME | ✅ GPGME |
| Generate Keypair | ❌ | ✅ GPG CLI |
| Change PIN | ❌ | ✅ GPG CLI |
| Delete Keypair | ❌ | ✅ GPG CLI |
| Card Status | ❌ | ✅ GPG CLI |
| Framework | ASP.NET Core | Vapor |
| Port | 5555 | 5555 |
| HTTPS | ✅ | ✅ (planned) |

## Contributing

This is part of the SmartPGP project. See the main repository README for contribution guidelines.

## License

Same license as the SmartPGP project.

## Related Documentation

- [Windows Helper](../windows/README.md)
- [Outlook Add-in](../../outlook_addin/README.md)
- [Outlook Web Helper Docs](../../docs/outlook_web_helper.md)
- [SmartPGP Card Documentation](../../README.md)
