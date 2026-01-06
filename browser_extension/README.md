# SmartPGP Bridge Browser Extension (Chrome/Firefox)

Purpose: enable Outlook Web users to call the local SmartPGP helper (encrypt/decrypt) by bypassing browser CORS/sandbox via extension permissions. Includes a floating widget inside outlook.office.com/outlook.live.com and a popup to set the helper URL.

## Structure
- `manifest.json` — Chrome/Chromium MV3
- `manifest.firefox.json` — Firefox MV2
- `background.js` — stores helper URL (sync storage)
- `contentScript.js` — injects floating widget; calls helper `/encrypt` and `/decrypt`
- `popup.html/js` — configure helper URL
- `icons/` — placeholder icons; replace with branded assets

## Load in Chrome/Edge (dev)
1) Open `chrome://extensions`, enable Developer mode.
2) “Load unpacked” → select `browser_extension/`.
3) Click the extension icon → set helper URL (default `https://127.0.0.1:5555`).
4) Open Outlook Web; a floating “SmartPGP Bridge” widget appears (bottom-right).

## Load in Firefox (dev)
1) Open `about:debugging#/runtime/this-firefox`.
2) “Load Temporary Add-on…” → select `browser_extension/manifest.firefox.json`.
3) Configure helper URL via the toolbar popup.
4) Open Outlook Web; floating widget appears.

## Usage
- Paste plaintext/ciphertext into the widget.
- For encryption, supply comma-separated recipients; calls helper `/encrypt` and renders armored output.
- For decryption, paste armored text; calls helper `/decrypt` and shows plaintext.

## Notes / Limitations
- This bypasses the CORS/localhost block but still requires the local SmartPGP helper running with HTTPS (self-signed cert is fine once trusted).
- Widget is intentionally minimal; deeper Outlook DOM integration (auto-reading/setting message body) can be added but risks fragility against Outlook UI changes.
- If your helper uses a non-default URL/port, set it in the popup; stored in `chrome.storage.sync`.
- Replace placeholder icons before packaging.***
