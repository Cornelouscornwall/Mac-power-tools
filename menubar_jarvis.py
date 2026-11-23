#!/usr/bin/env python3
"""Menu-bar JARVIS: click 🤖 in the menu bar, ask for anything. Risky actions ask first."""
import subprocess

import anthropic
import rumps

MODEL = "claude-sonnet-5-5"
client = anthropic.Anthropic()  # needs ANTHROPIC_API_KEY

SYSTEM = (
    "You are JARVIS, a witty, concise assistant living in the user's Mac menu bar. "
    "Use your tools to actually do things. Keep replies short."
)

TOOLS = [
    {
        "name": "open_app",
        "description": "Open a macOS application by name.",
        "input_schema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]},
    },
    {
        "name": "run_applescript",
        "description": "Run AppleScript to control Mac apps and settings.",
        "input_schema": {"type": "object", "properties": {"script": {"type": "string"}}, "required": ["script"]},
    },
    {
        "name": "run_shell",
        "description": "Run a shell command and return its output.",
        "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]},
    },
]


def confirm(what: str) -> bool:
    return rumps.alert(title="JARVIS wants to run:", message=what, ok="Allow", cancel="Deny") == 1


def run_tool(name: str, args: dict) -> str:
    try:
        if name == "open_app":
            r = subprocess.run(["open", "-a", args["name"]], capture_output=True, text=True)
        elif name == "run_applescript":
            if not confirm(args["script"]):
                return "User denied."
            r = subprocess.run(["osascript", "-e", args["script"]], capture_output=True, text=True, timeout=30)
        elif name == "run_shell":
            if not confirm(args["command"]):
                return "User denied."
            r = subprocess.run(args["command"], shell=True, capture_output=True, text=True, timeout=30)
        else:
            return f"Unknown tool: {name}"
        return (r.stdout + r.stderr).strip() or "Done."
    except Exception as e:  # noqa: BLE001
        return f"Error: {e}"


class JarvisApp(rumps.App):
    def __init__(self) -> None:
        super().__init__("🤖", quit_button="Quit")
        self.messages: list = []
        self.mute = False
        self.menu = [
            rumps.MenuItem("Ask Jarvis…", callback=self.ask, key="j"),
            rumps.MenuItem("Mute voice", callback=self.toggle_mute),
            rumps.MenuItem("Forget conversation", callback=self.forget),
        ]

    def toggle_mute(self, sender) -> None:
        sender.state = not sender.state
        self.mute = bool(sender.state)

    def forget(self, _) -> None:
        self.messages = []
        rumps.notification("JARVIS", "", "Conversation cleared.")

    def ask(self, _) -> None:
        win = rumps.Window(
            message="What can I do for you?", title="JARVIS", default_text="",
            ok="Send", cancel="Cancel", dimensions=(360, 24),
        )
        r = win.run()
        if not r.clicked or not r.text.strip():
            return
        self.messages.append({"role": "user", "content": r.text.strip()})

        while True:
            try:
                resp = client.messages.create(
                    model=MODEL, max_tokens=1024, system=SYSTEM, tools=TOOLS, messages=self.messages
                )
            except Exception as e:  # noqa: BLE001
                self.messages.pop()
                rumps.alert(title="JARVIS", message=f"Error: {e}")
                return
            self.messages.append({"role": "assistant", "content": resp.content})
            if resp.stop_reason != "tool_use":
                text = "".join(b.text for b in resp.content if b.type == "text").strip()
                if not self.mute:
                    subprocess.Popen(["say", text])
                rumps.alert(title="JARVIS", message=text)
                return
            results = [
                {"type": "tool_result", "tool_use_id": b.id, "content": run_tool(b.name, b.input)}
                for b in resp.content
                if b.type == "tool_use"
            ]
            self.messages.append({"role": "user", "content": results})


if __name__ == "__main__":
    JarvisApp().run()
