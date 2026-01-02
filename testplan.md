# SmartPGP Outlook Integration Test Plan (Windows + Firefox + PCSC + AEPGP)

## Scope
Step-by-step validation of the SmartPGP Outlook add-in and Windows helper using a PCSC smartcard reader with the AEPGP (SmartPGP) applet, run in Outlook on the web (Firefox) and localhost helper at `https://127.0.0.1:5555`.

## Prerequisites
- Hardware: PCSC-compatible reader; SmartPGP/AEPGP card inserted.
- Services: Windows Smart Card service (`sc query SCardSvr` shows RUNNING).
- Software: Gpg4win (GnuPG), .NET 8 SDK, Node.js 18+, PowerShell, Firefox.
- Keys: Recipient public key(s) imported into GnuPG; card-backed secret keys present for signing/decryption.

## GnuPG + PCSC Setup
1) Optional PCSC-only: create `%APPDATA%\gnupg\scdaemon.conf` with `disable-ccid`.  
2) Restart scdaemon: `gpgconf --kill scdaemon`.  
3) Verify card: `gpg --card-status`; list keys: `gpg --list-secret-keys`.  
4) Import recipient pubkeys: `gpg --import recipient.asc` (if needed).

## TLS Certificates (trust both Windows + Firefox)
1) Helper: `dotnet dev-certs https --trust` (or use `outlook_helper/windows/SmartPGP.OutlookHelper/scripts/new-dev-cert.ps1` and import the generated PFX into Windows Trusted Root + Firefox Authorities).  
2) Add-in host: `cd outlook_addin && npm install && npm run dev-cert`; import `outlook_addin/certs/addin-localhost.pfx` into Windows Trusted Root + Firefox Authorities (trust for websites).

## Start Services
1) Helper:  
   - `cd outlook_helper/windows/SmartPGP.OutlookHelper`  
   - `dotnet restore`  
   - `dotnet run` (listens on `https://127.0.0.1:5555`).  
   - Optional env vars: `SmartPgp__CertificatePath`, `SmartPgp__CertificatePassword`, `SmartPgp__Port`, `SmartPgp__AllowedOrigin`.
2) Add-in host:  
   - `cd outlook_addin`  
   - `npm start` (serves `https://localhost:3000`, manifest and assets).

## Local Self-Tests (PowerShell)
Run aggregator:  
`pwsh -File tools/selftest.ps1 -HelperUrl https://127.0.0.1:5555 -Recipient you@example.com -AddinHost https://localhost:3000`
- Verifies helper `/encrypt` + `/decrypt` round-trip vs gpg.
- Verifies add-in host serves `manifest.xml` and `functions.js`.

## Outlook on the Web (Firefox) Sideload
1) Open `https://outlook.office.com` in Firefox.  
2) Settings (gear) → “View all Outlook settings” → Mail → Customize actions → “Add-ins” → “My add-ins”.  
3) “Add a custom add-in” → “Add from URL” → enter `https://localhost:3000/manifest.xml` → confirm trust (cert must be trusted in Firefox).

## End-to-End Encrypt/Send
1) Compose a new email; add TO + CC + BCC recipients with known public keys.  
2) Body can be HTML or text (handler supports both).  
3) Click “SmartPGP Mail” → “Encrypt & Send” (or just send; OnMessageSend triggers).  
4) Expected: send succeeds; message body replaced with armored PGP; header `smartpgp-encrypted: 1` set.

## End-to-End Decrypt (Task Pane)
1) Open the received message in Firefox OWA.  
2) Click “SmartPGP Mail” → “Decrypt” to show the task pane.  
3) Expected: task pane detects header, calls `https://127.0.0.1:5555/decrypt`, displays plaintext.  
4) If helper is down, pane shows friendly availability error.

## PCSC / Reader Validation
- Monitor reader binding: `gpg-connect-agent "scd getinfo reader_list" /bye`.  
- If CCID is used instead of PCSC, add `disable-ccid` (above), restart scdaemon, re-run tests.

## Troubleshooting Checklist
- Cert trust errors: re-import PFX into Windows Trusted Root and Firefox Authorities; restart Firefox.  
- Helper unreachable: confirm `dotnet run` console output, port 5555, firewall exceptions.  
- Key not found: ensure recipient pubkey is imported; set `SmartPgp:SignerId` if signing required.  
- Send blocked: check error surfaced by OnMessageSend; ensure helper is running and cert trusted.  
- Decrypt fails: confirm `smartpgp-encrypted` header present and card PIN/reader is available.
