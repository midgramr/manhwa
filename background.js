console.log("background.js loaded");

function blobToDataURL(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

browser.runtime.onMessage.addListener(async (message) => {
  if (message.type !== "replace-image") return;

  const response = await fetch("http://127.0.0.1:8080/image", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      source: message.originalSrc
    })
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  const blob = await response.blob();
  return await blobToDataURL(blob);
});