#!/usr/bin/env python3
"""rewrite: reads text on stdin, prints the rewritten text on stdout.

Usage: rewrite.py [fix|shorten|formal|casual|translate:<Language>]
If anything goes wrong, the original text is printed back so a Quick Action
never replaces your selection with nothing.
"""
import sys

MODEL = "claude-sonnet-5-5"

MODES = {
    "fix": "Fix spelling, grammar and punctuation. Keep the meaning, tone and wording otherwise unchanged.",
    "shorten": "Make this shorter and punchier without losing the key points.",
    "formal": "Rewrite this in a polished, professional tone.",
    "casual": "Rewrite this in a relaxed, friendly tone.",
}


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "fix"
    text = sys.stdin.read()
    if not text.strip():
        return
    try:
        if mode.startswith("translate:"):
            instruction = f"Translate this into {mode.split(':', 1)[1]}."
        else:
            instruction = MODES[mode]
        import anthropic  # inside try: a missing package must not wipe your text

        client = anthropic.Anthropic()  # needs ANTHROPIC_API_KEY
        resp = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            system=f"{instruction} Output only the resulting text, nothing else.",
            messages=[{"role": "user", "content": text}],
        )
        sys.stdout.write(resp.content[0].text.strip())
    except Exception as e:  # noqa: BLE001
        print(f"rewrite error: {e}", file=sys.stderr)
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
