console.log("page-hook.js loaded");

window.toggle = false;

(() => {
  if(window.toggle) return;
  const originalCreateImageBitmap = window.createImageBitmap;
  const pendingRequests = new Map();
  const replacementCache = new Map();
  let nextRequestId = 1;

  function requestReplacement(originalSrc) {
    if (replacementCache.has(originalSrc)) {
      return replacementCache.get(originalSrc);
    }

    const promise = new Promise((resolve, reject) => {
      const requestId = nextRequestId++;
      pendingRequests.set(requestId, { resolve, reject, originalSrc });

      window.postMessage({
        type: "TOPTOON_REQUEST_REPLACEMENT",
        requestId,
        originalSrc
      }, "*");
    });

    replacementCache.set(originalSrc, promise);
    return promise;
  }

  function loadImage(url) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = "anonymous";
      img.onload = () => resolve(img);
      img.onerror = (e) => reject(new Error("Failed to load image: " + url));
      img.src = url;
    });
  }

  window.addEventListener("message", (event) => {
    if(window.toggle) return;
    if (event.source !== window) return;
    if (!event.data || event.data.type !== "TOPTOON_RESPONSE_REPLACEMENT") return;

    const pending = pendingRequests.get(event.data.requestId);
    if (!pending) return;

    pendingRequests.delete(event.data.requestId);

    if (event.data.error || !event.data.replacementUrl) {
      console.error("replacement response failed", event.data.error);
      replacementCache.delete(pending.originalSrc);
      pending.reject(new Error(event.data.error || "No replacement URL"));
      return;
    }

    loadImage(event.data.replacementUrl)
      .then((img) => {
        console.log("replacement image loaded for", pending.originalSrc);
        pending.resolve(img);
      })
      .catch((err) => {
        console.error("replacement image load failed", err);
        replacementCache.delete(pending.originalSrc);
        pending.reject(err);
      });
  });

  window.createImageBitmap = async function (...args) {
    const source = args[0];

    try {
      if (source instanceof HTMLImageElement && source.src) {
        const originalSrc = source.src;
        console.log("intercepted createImageBitmap for", originalSrc);

        const replacementImg = await requestReplacement(originalSrc);

        const newArgs = [...args];
        newArgs[0] = replacementImg;

        console.log("using replacement image for", originalSrc);
        return originalCreateImageBitmap.apply(this, newArgs);
      }
    } catch (err) {
      console.error("createImageBitmap replacement failed, falling back", err);
    }

    return originalCreateImageBitmap.apply(this, args);
  };

  console.log("createImageBitmap hook installed");
})();