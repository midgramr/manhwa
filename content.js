console.log("content.js loaded");
window.toggle = false;

const script = document.createElement("script");
script.defer = true;
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
  if (event.data?.type === "TOGGLE_UPDATE"){
    window.toggle = !window.toggle
    return;
  }
    if (window.toggle) return
  if (!event.data || event.data.type !== "TOPTOON_REQUEST_REPLACEMENT") return;

  try {
    const replacementUrl = await browser.runtime.sendMessage({
      type: "replace-image",
      originalSrc: event.data.originalSrc
    });

    window.postMessage(
      {
        type: "TOPTOON_RESPONSE_REPLACEMENT",
        requestId: event.data.requestId,
        replacementUrl
      },
      "*"
    );
  } catch (err) {
    window.postMessage(
      {
        type: "TOPTOON_RESPONSE_REPLACEMENT",
        requestId: event.data.requestId,
        error: String(err)
      },
      "*"
    );
  }
});

const DIRECT_IMG_SELECTOR = "div.comic_img.c_img img.document_img";
const DIRECT_IMG_REPLACED_ATTR = "data-toptoon-direct-replaced";
const directReplacementCache = new Map();

async function getReplacementUrl(originalSrc) {
  if (!originalSrc) return null;

  if (directReplacementCache.has(originalSrc)) {
    return directReplacementCache.get(originalSrc);
  }

  const promise = browser.runtime.sendMessage({
    type: "replace-image",
    originalSrc
  });

  directReplacementCache.set(originalSrc, promise);

  try {
    return await promise;
  } catch (err) {
    directReplacementCache.delete(originalSrc);
    throw err;
  }
}

async function replaceDocumentImage(img) {
  if(window.toggle) return
  if (!img) return;
  if (img.getAttribute(DIRECT_IMG_REPLACED_ATTR) === "true") return;

  const originalSrc = img.currentSrc || img.src;
  if (!originalSrc) return;

  try {
    const replacementUrl = await getReplacementUrl(originalSrc);

    if (!replacementUrl) {
      console.warn("No replacement image returned for:", originalSrc);
      return;
    }

    // Replace only this DOM image element.
    img.src = replacementUrl;
    img.removeAttribute("srcset");
    img.srcset = "";
    img.setAttribute(DIRECT_IMG_REPLACED_ATTR, "true");

    console.log("Directly replaced document_img:", originalSrc);
  } catch (error) {
    console.error("Failed to replace document_img:", error);
  }
}

function scanAndReplaceDocumentImages(root = document) {
  const images = root.querySelectorAll(DIRECT_IMG_SELECTOR);
  for (const img of images) {
    replaceDocumentImage(img);
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    scanAndReplaceDocumentImages();
  });
} else {
  scanAndReplaceDocumentImages();
}

const directImageObserver = new MutationObserver((mutations) => {
  for (const mutation of mutations) {
    for (const node of mutation.addedNodes) {
      if (!(node instanceof Element)) continue;

      if (node.matches?.(DIRECT_IMG_SELECTOR)) {
        replaceDocumentImage(node);
      }

      scanAndReplaceDocumentImages(node);
    }
  }
});

directImageObserver.observe(document.documentElement, {
  childList: true,
  subtree: true
});