(() => {
  const WIDGET_ID = "smartpgp-bridge-widget";
  const DEFAULT_HELPER_URL = "https://127.0.0.1:5555";
  let helperUrl = DEFAULT_HELPER_URL;

  chrome.runtime.sendMessage({ type: "getHelperUrl" }, (resp) => {
    helperUrl = resp?.helperUrl || DEFAULT_HELPER_URL;
  });

  function createWidget() {
    if (document.getElementById(WIDGET_ID)) return;

    const container = document.createElement("div");
    container.id = WIDGET_ID;
    Object.assign(container.style, {
      position: "fixed",
      bottom: "16px",
      right: "16px",
      width: "320px",
      background: "#0f172a",
      color: "#e2e8f0",
      borderRadius: "12px",
      boxShadow: "0 12px 28px rgba(0,0,0,0.25)",
      padding: "12px",
      fontFamily: "Inter, system-ui, sans-serif",
      zIndex: 999999
    });

    container.innerHTML = `
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
        <div style="font-weight:700;font-size:14px;">SmartPGP Bridge</div>
        <button id="smartpgp-close" style="background:none;border:none;color:#94a3b8;font-size:16px;cursor:pointer;">×</button>
      </div>
      <div style="font-size:12px;color:#cbd5e1;margin-bottom:6px;">Paste text to encrypt/decrypt via local helper.</div>
      <textarea id="smartpgp-input" style="width:100%;height:90px;background:#1e293b;color:#e2e8f0;border:1px solid #334155;border-radius:8px;padding:8px;resize:vertical;"></textarea>
      <div style="display:flex;gap:8px;margin:8px 0;">
        <input id="smartpgp-recipients" placeholder="Recipients (comma-separated)" style="flex:1;background:#1e293b;color:#e2e8f0;border:1px solid #334155;border-radius:8px;padding:6px 8px;font-size:12px;" />
      </div>
      <div style="display:flex;gap:8px;margin-bottom:8px;">
        <button id="smartpgp-encrypt" style="flex:1;background:#10b981;border:none;color:#0b1727;border-radius:8px;padding:8px;font-weight:700;cursor:pointer;">Encrypt</button>
        <button id="smartpgp-decrypt" style="flex:1;background:#3b82f6;border:none;color:#0b1727;border-radius:8px;padding:8px;font-weight:700;cursor:pointer;">Decrypt</button>
      </div>
      <div id="smartpgp-status" style="font-size:11px;color:#f8fafc;margin-bottom:6px;"></div>
      <textarea id="smartpgp-output" readonly style="width:100%;height:90px;background:#0b1220;color:#e2e8f0;border:1px solid #334155;border-radius:8px;padding:8px;resize:vertical;"></textarea>
    `;

    document.body.appendChild(container);

    container.querySelector("#smartpgp-close").onclick = () => container.remove();
    container.querySelector("#smartpgp-encrypt").onclick = () => runOperation("encrypt");
    container.querySelector("#smartpgp-decrypt").onclick = () => runOperation("decrypt");
  }

  async function runOperation(mode) {
    const input = document.getElementById("smartpgp-input").value || "";
    const recipientsRaw = document.getElementById("smartpgp-recipients").value || "";
    const recipients = recipientsRaw.split(",").map(r => r.trim()).filter(Boolean);
    const statusEl = document.getElementById("smartpgp-status");
    const outputEl = document.getElementById("smartpgp-output");

    if (!input.trim()) {
      statusEl.textContent = "Nothing to process.";
      return;
    }
    if (mode === "encrypt" && recipients.length === 0) {
      statusEl.textContent = "Enter at least one recipient.";
      return;
    }

    statusEl.textContent = `${mode === "encrypt" ? "Encrypting" : "Decrypting"} via ${helperUrl} ...`;
    try {
      const body =
        mode === "encrypt"
          ? { body: input, recipients }
          : { body: input };
      const resp = await fetch(`${helperUrl}/${mode}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      if (!resp.ok) {
        const text = await resp.text();
        throw new Error(text || `HTTP ${resp.status}`);
      }
      const json = await resp.json();
      outputEl.value = mode === "encrypt" ? json.armored || "" : json.plaintext || "";
      statusEl.textContent = "Done.";
    } catch (err) {
      outputEl.value = "";
      statusEl.textContent = `Error: ${err?.message || err}`;
    }
  }

  // Inject widget when user is on Outlook Web
  if (location.hostname.includes("outlook.office.com") || location.hostname.includes("outlook.live.com")) {
    createWidget();
  }
})();
