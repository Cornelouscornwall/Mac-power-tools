# 🛠️ mac-power-tools

Three AI-powered macOS tools, all powered by Claude.

## Setup
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-key-here
```

## 1. ✍️ rewriter: fix or rewrite text in any app
`rewriter/rewrite.py` reads text on stdin and prints the result. Modes: `fix`, `shorten`, `formal`, `casual`, `translate:Spanish`.

Make it a system-wide hotkey:
1. Open **Automator** → New Document → **Quick Action**.
2. Set "Workflow receives current **text** in **any application**" and tick **Output replaces selected text**.
3. Add a **Run Shell Script** action: shell `/bin/zsh`, pass input **to stdin**, script:
   ```
   source ~/.zshrc; /full/path/to/.venv/bin/python /full/path/to/rewriter/rewrite.py fix
   ```
4. Save it as "Fix text". Then go to **System Settings → Keyboard → Keyboard Shortcuts → Services → Text** and give it a shortcut.

Make one Quick Action per mode (shorten, formal, ...). If the API call fails, your original text is kept.

## 2. 📸 screenshot-explainer
```bash
python screenshot-explainer/explain.py
python screenshot-explainer/explain.py "translate this to English"
```
Drag a box around anything on screen (Esc cancels). The answer shows in a dialog and is copied to your clipboard. Your terminal app needs **Screen Recording** permission (System Settings → Privacy & Security).

## 3. 🤖 menubar-jarvis
```bash
python menubar-jarvis/menubar_jarvis.py
```
A 🤖 appears in your menu bar. Opening apps runs freely; AppleScript and shell commands pop up an **Allow / Deny** dialog first. Add it to **Login Items** if you want it always on.

## Privacy
Only the text you select (rewriter), the area you capture (explainer) and what you type (menu-bar Jarvis) is sent to the API.
