#!/usr/bin/env python3
"""explain: drag a box around anything on screen and Claude explains or solves it.

Usage: explain.py [optional question about the screenshot]
"""
import base64
import os
import subprocess
import sys
import tempfile

import anthropic

MODEL = "claude-sonnet-5-5"
DEFAULT_Q = (
    "Explain what's in this screenshot. If it contains a question, problem or error, "
    "solve it or explain the fix. Be concise."
)


def main() -> None:
    question = " ".join(sys.argv[1:]) or DEFAULT_Q
    path = os.path.join(tempfile.gettempdir(), "explain_shot.png")
    if os.path.exists(path):
        os.remove(path)

    subprocess.run(["screencapture", "-i", "-x", path])  # drag to select; Esc cancels
    if not os.path.exists(path):
        sys.exit("No screenshot taken.")
    subprocess.run(["sips", "-Z", "1568", path], capture_output=True)  # shrink big screens

    with open(path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode()
    os.remove(path)

    client = anthropic.Anthropic()  # needs ANTHROPIC_API_KEY
    resp = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": data}},
                    {"type": "text", "text": question},
                ],
            }
        ],
    )
    answer = "".join(b.text for b in resp.content if b.type == "text").strip()
    print(answer)
    subprocess.run(["pbcopy"], input=answer, text=True)  # also copied to your clipboard
    subprocess.run(
        [
            "osascript",
            "-e", "on run argv",
            "-e", 'display dialog (item 1 of argv) with title "Screenshot Explainer" buttons {"OK"} default button "OK"',
            "-e", "end run",
            answer[:1200],
        ]
    )


if __name__ == "__main__":
    main()
