console.log("content.js loaded");

const script = document.createElement("script");
script.src = browser.runtime.getURL("page-hook.js");
script.onload = () => {
  console.log("page-hook injected successfully");
  script.remove();
};
script.onerror = (e) => {
  console.error("page-hook failed to load", e);
};
(document.head || document.documentElement).appendChild(script);

window.addEventListener("message", async (event) => {
  if (event.source !== window) return;
  if (!event.data || event.data.type !== "TOPTOON_REQUEST_REPLACEMENT") return;

  try {
    const replacementUrl = await browser.runtime.sendMessage({
      type: "replace-image",
      originalSrc: event.data.originalSrc
    });

    window.postMessage({
      type: "TOPTOON_RESPONSE_REPLACEMENT",
      requestId: event.data.requestId,
      replacementUrl
    }, "*");
  } catch (err) {
    window.postMessage({
      type: "TOPTOON_RESPONSE_REPLACEMENT",
      requestId: event.data.requestId,
      error: String(err)
    }, "*");
  }
});