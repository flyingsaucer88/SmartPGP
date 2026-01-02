# SmartPGP ↔ Outlook Web Integration – Starter Notes

These notes anchor the first implementation steps for the Outlook add-in flow described in the gist. They focus on the Windows localhost helper and how it will talk to the SmartPGP/AEPGP card via GnuPG.

## Scope for first implementation
- Deliver a localhost HTTPS helper on Windows that exposes `POST /encrypt` and `POST /decrypt` (JSON in/out).
- Use GnuPG/GPGME so the card handles all private-key operations; no PINs or keys flow through the add-in.
- Keep the helper bound to `127.0.0.1` with a trusted localhost cert and CORS locked to the add-in origin.
- Align ciphertext format with standard OpenPGP messages (armored or PGP/MIME) so Outlook and other PGP tools interoperate; do **not** reuse the custom AES-GCM envelope from the Windows shell handlers.

## API contract (initial)
- `POST /encrypt` → body: `{ "body": "<plaintext>", "recipients": ["alice@example.com"] }` → response: `{ "armored": "<-----BEGIN PGP MESSAGE----->" }`.
- `POST /decrypt` → body: `{ "body": "<armored pgp message>" }` → response: `{ "plaintext": "<decrypted text>" }`.
- Add-on sets internet header `smartpgp-encrypted: 1` on send; task pane checks it before decrypting.

## Card + GnuPG expectations
- SmartPGP card must already hold the keys; GnuPG smartcard support uses `PSO:DECIPHER` with PKCS#1 v1.5, matching the applet.
- Helper should rely on GnuPG to select the right key by recipient email or key ID; PIN entry is handled by gpg-agent/pinentry.
- Verify base plumbing before wiring Outlook:
  1) `gpg --card-status`
  2) `gpg --decrypt <sample>` and `gpg --sign` using the card
  3) `gpg --list-secret-keys` shows the card-backed keys

## Implementation Status

### Completed ✅
1) ✅ Scaffolded Windows helper (`outlook_helper/windows`) with full GPGME integration (not placeholders)
2) ✅ CORS + HTTPS (localhost cert) configured with loopback binding
3) ✅ Interop test suite implemented (`outlook_helper/windows/SmartPGP.OutlookHelper/tests/selftest.ps1`)
4) ✅ Add-in manifest/assets created with OnMessageSend handler
5) ✅ Add-in extracts TO, CC, and BCC recipients (per gist requirements)
6) ✅ Add-in supports both HTML and text body formats
7) ✅ Graceful error handling for helper unavailability

### Remaining Tasks
- Author comprehensive "developer setup" doc (GnuPG install, smartcard driver check, cert trust)
- Create icon assets for add-in manifest (16x16, 32x32, 64x64, 80x80 PNGs)
- Test end-to-end flow with actual SmartPGP card
- macOS helper implementation
- MSI/installer packaging for production deployment
