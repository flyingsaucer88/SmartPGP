const DEFAULT_HELPER_URL = "https://127.0.0.1:5555";

const helperInput = document.getElementById("helper-url");
const statusEl = document.getElementById("status");

chrome.storage.sync.get({ helperUrl: DEFAULT_HELPER_URL }, (data) => {
  helperInput.value = data.helperUrl || DEFAULT_HELPER_URL;
});

document.getElementById("save").onclick = () => {
  const url = helperInput.value.trim() || DEFAULT_HELPER_URL;
  chrome.storage.sync.set({ helperUrl: url }, () => {
    statusEl.textContent = `Saved: ${url}`;
  });
};
