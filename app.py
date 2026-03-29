from flask import Flask, request, send_file
from flask_cors import CORS
import requests
import os
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

@app.route("/image", methods=["POST"])
def image():
    data = request.get_json()
    source = data.get("source") if data else None
    if not source:
        return "missing source", 400

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://toptoon.com/"
    }

    resp = requests.get(source, headers=headers, timeout=15)
    print(source)
    resp.raise_for_status()
    
    content_type = resp.headers.get("Content-Type", "")

    ext = content_type.split("/")[-1].split(";")[0]
    if ext == "jpeg":
        ext = "jpg"

    os.makedirs("downloads", exist_ok=True)
    filename = f"downloads/image-{source}.{ext}"

    with open(filename, "wb") as f:
        f.write(resp.content)
        
    return send_file(
        "image.jpg",
        mimetype=resp.headers.get("Content-Type", "image/jpeg")
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)