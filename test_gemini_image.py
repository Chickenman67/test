import base64
import os
import sys

import requests

MODEL = "gemini-2.5-flash-image"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"


def main() -> None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable is not set.")
        sys.exit(1)

    prompt = "A simple stick figure man, drawn in thin black lines on a plain white background."

    body = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    resp = requests.post(
        URL,
        params={"key": api_key},
        json=body,
        timeout=120,
    )

    if resp.status_code != 200:
        print(f"ERROR: request failed with status {resp.status_code}")
        print(resp.text)
        sys.exit(1)

    candidates = resp.json().get("candidates", [])
    if not candidates:
        print("ERROR: no candidates in response")
        print(resp.text)
        sys.exit(1)

    parts = candidates[0]["content"]["parts"]
    images = [
        p["inlineData"] for p in parts
        if p.get("inlineData", {}).get("data")
    ]

    if not images:
        print("ERROR: response contained no image data")
        print(resp.text)
        sys.exit(1)

    for i, inline in enumerate(images):
        data = base64.b64decode(inline["data"])
        filename = f"test_output_{i + 1}.png"
        with open(filename, "wb") as f:
            f.write(data)
        print(f"Saved {filename} ({len(data)} bytes, {inline.get('mimeType', 'image/png')})")


if __name__ == "__main__":
    main()