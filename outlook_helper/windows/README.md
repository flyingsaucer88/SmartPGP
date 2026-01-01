# SmartPGP Outlook Helper (Windows) – Skeleton

This directory contains a starter ASP.NET Core minimal API that will act as the localhost bridge between the Outlook add-in and the SmartPGP card (via GnuPG/GPGME).

## Status
- API surface (`/encrypt`, `/decrypt`, `/healthz`) is scaffolded in `SmartPGP.OutlookHelper/Program.cs`.
- Crypto calls are **not implemented yet**; `PgpService` returns a placeholder until GPGME wiring is added.

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

## Interop test plan (manual)
1) Verify card + gpg: `gpg --card-status` and `gpg --decrypt <ciphertext>` works.
2) Run helper: `dotnet run`.
3) Encrypt via helper:
   - `curl -k -X POST https://127.0.0.1:5555/encrypt -H "Content-Type: application/json" -d '{"body":"hello","recipients":["you@example.com"]}'`
   - Save `armored` output to `test.asc`.
4) Decrypt via helper:
   - `curl -k -X POST https://127.0.0.1:5555/decrypt -H "Content-Type: application/json" --data-binary @test.asc` (wrap in JSON: `{"body":"<contents>"}`).
5) Cross-check with GnuPG: `gpg --decrypt test.asc` should match the helper’s decrypt result.
