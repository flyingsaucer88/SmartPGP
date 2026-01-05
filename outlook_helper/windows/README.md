# SmartPGP Outlook Helper for Windows

A localhost HTTPS server that provides PGP encryption, decryption, and card management operations for SmartPGP cards on Windows. This helper enables Outlook add-ins and other applications to interact with SmartPGP hardware tokens.

## Features

- **Encryption/Decryption**: Standard OpenPGP encryption and decryption using GPGME
- **Card Management**: Generate keypairs, change PIN, delete keys (factory reset)
- **Card Status**: Query card information and key status
- **Security**: Localhost-only binding, CORS protection, hardware-backed private keys
- **Compatibility**: Works with standard OpenPGP cards and SmartPGP tokens

## Prereqs (expected)
- .NET 8 SDK
- GnuPG/Gpg4win installed and working with the SmartPGP card (`gpg --card-status`, `gpg --decrypt` with the card)
- GPGME bindings for .NET (e.g., gpgme-sharp) available to reference once added to the project

## Running (dev)
```bash
cd outlook_helper/windows/SmartPGP.OutlookHelper
dotnet run
```
- Default port: `5555` (override with `SmartPgp:Port` in config/environment).
- CORS origin: `https://localhost` by default (set `SmartPgp:AllowedOrigin`).
- HTTPS: uses ASP.NET Core dev cert unless `SmartPgp:CertificatePath` and `SmartPgp:CertificatePassword` are provided.

## Configuration
- `appsettings.json` holds defaults (port 5555, `AllowedOrigin`, `certs/localhost.pfx`, optional `SignerId`).
- Override with environment vars:
  - `SmartPgp__Port`
  - `SmartPgp__AllowedOrigin`
  - `SmartPgp__CertificatePath`
  - `SmartPgp__CertificatePassword`
  - `SmartPgp__SignerId`

## Localhost certificate
- Generate a dev cert: `powershell -ExecutionPolicy Bypass -File scripts/new-dev-cert.ps1`
- Trust it (Current User > Trusted Root) and update `CertificatePassword` in config/env.

## API Endpoints

### Encryption & Decryption

**POST /encrypt**
```json
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

**POST /decrypt**
```json
Request:
{
  "body": "-----BEGIN PGP MESSAGE-----\n..."
}

Response:
{
  "plaintext": "decrypted message"
}
```

### Card Management

**POST /generate-keypair** (30-120 seconds)
```json
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

**POST /change-pin**
```json
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

**POST /delete-keypair** (Factory Reset - Irreversible!)
```json
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

**GET /card-status**
```json
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

**GET /healthz**
```
Response: "ok"
```

## Testing

### Manual Test Plan
1) Verify card + gpg: `gpg --card-status` and `gpg --decrypt <ciphertext>` works.
2) Run helper: `dotnet run`.
3) Test encryption:
   ```powershell
   curl -k -X POST https://127.0.0.1:5555/encrypt `
     -H "Content-Type: application/json" `
     -d '{"body":"hello","recipients":["you@example.com"]}'
   ```
4) Test decryption:
   ```powershell
   curl -k -X POST https://127.0.0.1:5555/decrypt `
     -H "Content-Type: application/json" `
     -d '{"body":"-----BEGIN PGP MESSAGE-----\n..."}'
   ```
5) Cross-check with GnuPG: `gpg --decrypt test.asc` should match the helper's decrypt result.

### Card Management Tests
```powershell
# Card status
curl -k https://127.0.0.1:5555/card-status

# Generate keypair (takes 30-120 seconds)
curl -k -X POST https://127.0.0.1:5555/generate-keypair `
  -H "Content-Type: application/json" `
  -d '{"keySize":2048,"adminPin":"12345678"}'

# Change PIN
curl -k -X POST https://127.0.0.1:5555/change-pin `
  -H "Content-Type: application/json" `
  -d '{"currentPin":"123456","newPin":"newpin123"}'
```

## Comparison with macOS Version

| Feature | Windows (.NET) | macOS (Swift) |
|---------|---------------|---------------|
| Encryption | ✅ GPGME | ✅ GPGME |
| Decryption | ✅ GPGME | ✅ GPGME |
| Generate Keypair | ✅ GPG CLI | ✅ GPG CLI |
| Change PIN | ✅ GPG CLI | ✅ GPG CLI |
| Delete Keypair | ✅ GPG CLI | ✅ GPG CLI |
| Card Status | ✅ GPG CLI | ✅ GPG CLI |
| Framework | ASP.NET Core | Vapor |
| Port | 5555 | 5555 |
| HTTPS | ✅ | ✅ (planned) |

Both versions now have feature parity!
