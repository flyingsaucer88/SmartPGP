/* global Office */

const HELPER_URL = "https://127.0.0.1:5555";

Office.onReady(() => {
  // no-op
});

Office.actions.associate("onMessageSendHandler", onMessageSendHandler);
Office.actions.associate("encryptAndSend", onMessageSendHandler);
Office.actions.associate("showDecryptPane", showDecryptPane);

async function onMessageSendHandler(event) {
  try {
    const item = Office.context.mailbox.item;

    const bodyText = await getBodyText(item);
    const recipients = await getRecipients(item);

    const encrypted = await helperEncrypt(bodyText, recipients);

    await setBodyText(item, encrypted);
    await setHeader(item, "smartpgp-encrypted", "1");

    event.completed({ allowEvent: true });
  } catch (err) {
    const message = err && err.message ? err.message : "SmartPGP encryption failed.";
    event.completed({ allowEvent: false, errorMessage: message });
  }
}

async function showDecryptPane(event) {
  // Placeholder: actual UI is in taskpane.html; you can trigger display logic here if needed.
  event.completed();
}

async function helperEncrypt(body, recipients) {
  const response = await fetch(`${HELPER_URL}/encrypt`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ body, recipients })
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Helper encrypt failed: ${text}`);
  }
  const json = await response.json();
  return json.armored;
}

async function helperDecrypt(body) {
  const response = await fetch(`${HELPER_URL}/decrypt`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ body })
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Helper decrypt failed: ${text}`);
  }
  const json = await response.json();
  return json.plaintext;
}

function getBodyText(item) {
  return new Promise((resolve, reject) => {
    item.body.getAsync("text", result => {
      if (result.status === Office.AsyncResultStatus.Succeeded) {
        resolve(result.value || "");
      } else {
        reject(result.error);
      }
    });
  });
}

function setBodyText(item, text) {
  return new Promise((resolve, reject) => {
    item.body.setAsync(text, { coercionType: "text" }, result => {
      if (result.status === Office.AsyncResultStatus.Succeeded) {
        resolve();
      } else {
        reject(result.error);
      }
    });
  });
}

function getRecipients(item) {
  return new Promise((resolve, reject) => {
    item.to.getAsync(result => {
      if (result.status === Office.AsyncResultStatus.Succeeded) {
        const emails = (result.value || []).map(r => r.emailAddress);
        resolve(emails);
      } else {
        reject(result.error);
      }
    });
  });
}

function setHeader(item, name, value) {
  return new Promise((resolve, reject) => {
    item.internetHeaders.setAsync({ [name]: value }, result => {
      if (result.status === Office.AsyncResultStatus.Succeeded) {
        resolve();
      } else {
        reject(result.error);
      }
    });
  });
}

// Task pane helper to render decrypted text
async function decryptCurrentMessage() {
  const item = Office.context.mailbox.item;

  const headers = await new Promise((resolve, reject) => {
    item.internetHeaders.getAsync(["smartpgp-encrypted"], result => {
      if (result.status === Office.AsyncResultStatus.Succeeded) {
        resolve(result.value || {});
      } else {
        reject(result.error);
      }
    });
  });

  if (headers["smartpgp-encrypted"] !== "1") {
    updatePane("This message is not SmartPGP encrypted.");
    return;
  }

  const cipherBody = await getBodyText(item);
  const plaintext = await helperDecrypt(cipherBody);
  updatePane(plaintext);
}

function updatePane(text) {
  const el = document.getElementById("smartpgp-output");
  if (el) {
    el.textContent = text;
  }
}

window.decryptCurrentMessage = decryptCurrentMessage;
