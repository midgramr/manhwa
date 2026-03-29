console.log("background.js loaded");

async function imageUrlToBase64(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch original image: ${response.status}`);
  }

  const blob = await response.blob();

  return await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const dataUrl = reader.result; // "data:image/png;base64,...."
      const base64 = dataUrl.split(",")[1]; // remove data URL prefix
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

browser.runtime.onMessage.addListener(async (message) => {
  if (message.type !== "replace-image") return;

  const base64Image = await imageUrlToBase64(message.originalSrc);

  const response = await fetch("http://127.0.0.1:8000/translate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      image: base64Image
    })
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  const data = await response.json();

  // convert returned base64 back into a data URL the page can use
  return `data:image/png;base64,${data.image}`;
});