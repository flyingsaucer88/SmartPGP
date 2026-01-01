const fs = require("fs");
const path = require("path");
const https = require("https");
const express = require("express");
const cors = require("cors");

const PORT = process.env.PORT ? Number(process.env.PORT) : 3000;
const CERT_PATH = process.env.CERT_PATH || path.join(__dirname, "certs", "addin-localhost.pfx");
const CERT_PASSWORD = process.env.CERT_PASSWORD || "change-me";

const app = express();
app.use(cors());

// Serve static assets (functions.js, taskpane.html, etc.)
app.use(express.static(path.join(__dirname, "web")));

// Serve manifest from root
app.get("/manifest.xml", (req, res) => {
  res.sendFile(path.join(__dirname, "manifest", "manifest.xml"));
});

function start() {
  if (!fs.existsSync(CERT_PATH)) {
    console.error(`Certificate not found at ${CERT_PATH}. Run: npm run dev-cert`);
    process.exit(1);
  }

  const options = {
    pfx: fs.readFileSync(CERT_PATH),
    passphrase: CERT_PASSWORD
  };

  https.createServer(options, app).listen(PORT, () => {
    console.log(`SmartPGP add-in host listening on https://localhost:${PORT}`);
    console.log(`Manifest: https://localhost:${PORT}/manifest.xml`);
  });
}

start();
