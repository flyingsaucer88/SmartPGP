const https = require("https");

const HOST = process.env.ADDIN_HOST || "https://localhost:3000";

function fetchPath(path) {
  return new Promise((resolve, reject) => {
    https
      .get(`${HOST}${path}`, { rejectUnauthorized: false }, res => {
        const { statusCode } = res;
        if (statusCode !== 200) {
          reject(new Error(`GET ${path} failed: ${statusCode}`));
          res.resume();
          return;
        }
        res.on("data", () => {});
        res.on("end", () => resolve());
      })
      .on("error", reject);
  });
}

async function main() {
  try {
    console.log(`Self-test against add-in host ${HOST}`);
    await fetchPath("/manifest.xml");
    console.log("✓ manifest.xml reachable");
    await fetchPath("/functions.js");
    console.log("✓ functions.js reachable");
    console.log("PASS");
    process.exit(0);
  } catch (err) {
    console.error("FAIL:", err.message);
    process.exit(1);
  }
}

main();
