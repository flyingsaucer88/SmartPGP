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

## Immediate tasks
1) Scaffold the Windows helper (see `outlook_helper/windows`) with a minimal API surface and placeholder GPGME calls.
2) Add CORS + HTTPS (localhost cert) and lock listening to loopback.
3) Provide a small interop test: helper encrypts to your recipient key; `gpg --decrypt` succeeds; reverse flow also works.
4) Author a short “developer setup” doc (GnuPG install, smartcard driver check, cert trust) once the helper builds.

## Out of scope for now
- macOS helper, MSI/installer packaging, and Outlook add-in manifest/assets; those will follow once the Windows helper is proven.
