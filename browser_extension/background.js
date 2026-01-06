const DEFAULT_HELPER_URL = "https://127.0.0.1:5555";

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "getHelperUrl") {
    chrome.storage.sync.get({ helperUrl: DEFAULT_HELPER_URL }, (data) => {
      sendResponse({ helperUrl: data.helperUrl || DEFAULT_HELPER_URL });
    });
    return true;
  }

  if (message.type === "setHelperUrl" && message.helperUrl) {
    chrome.storage.sync.set({ helperUrl: message.helperUrl.trim() || DEFAULT_HELPER_URL }, () => {
      sendResponse({ ok: true });
    });
    return true;
  }
});
