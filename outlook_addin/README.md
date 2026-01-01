# SmartPGP Outlook Add-in Host (Dev)

This is a lightweight HTTPS static host for the add-in assets and manifest to speed up OWA testing.

## Prereqs
- Node 18+ and npm
- A trusted localhost certificate (self-signed is fine for dev)

## Setup
```bash
cd outlook_addin
npm install
npm run dev-cert   # generates certs/addin-localhost.pfx (password: change-me)
```
- Trust the generated cert (Current User > Trusted Root). If you use a different password/path, set env vars: `CERT_PASSWORD`, `CERT_PATH`.

## Run
```bash
npm start
# Host: https://localhost:3000
# Manifest: https://localhost:3000/manifest.xml
```

## Sideload (OWA quick path)
1) Start the host (`npm start`).
2) In Outlook on the web, add an add-in → Upload custom apps → paste `https://localhost:3000/manifest.xml`.
3) Compose an email and use the SmartPGP button; send handler calls the helper at `https://127.0.0.1:5555`.

## Notes
- The manifest references `https://localhost` URLs; ensure the host matches or update `manifest/manifest.xml`.
- Helper must be running (port 5555 by default) and trusted. Update `functions.js` if you change ports.
