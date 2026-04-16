#!/usr/bin/env python3
import sys
import os
import json
import random
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
CONFIG_PATH = SCRIPT_DIR / "curry.config.json"

# Read stdin before self-detaching — Claude Code passes JSON event data here.
_stdin_data: dict = {}
if not os.environ.get("CURRY_DETACHED"):
    try:
        raw = sys.stdin.read(4096)
        if raw.strip():
            _stdin_data = json.loads(raw)
    except Exception:
        pass

_tool_name = _stdin_data.get("tool_name", os.environ.get("CURRY_TOOL", ""))
_notif_msg = _stdin_data.get("message",   os.environ.get("CURRY_MSG",  ""))

# Fork a detached child and exit immediately so the hook doesn't block Claude Code.
if not os.environ.get("CURRY_DETACHED"):
    subprocess.Popen(
        [sys.executable, __file__] + sys.argv[1:],
        env={**os.environ, "CURRY_DETACHED": "1", "CURRY_TOOL": _tool_name, "CURRY_MSG": _notif_msg},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    sys.exit(0)


def _load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}


def _notify(title: str, body: str) -> None:
    t = title.replace('"', '\\"').replace("'", "\\'")
    b = body.replace('"',  '\\"').replace("'", "\\'")
    try:
        subprocess.run(
            ["osascript", "-e", f'display notification "{b}" with title "{t}"'],
            capture_output=True, timeout=4,
        )
    except Exception:
        pass
    print(f"🏀  {title} — {body}", file=sys.stderr)


def _play_sound(path: str | None) -> None:
    if not path:
        return
    p = Path(path)
    if not p.is_absolute():
        p = SCRIPT_DIR / p
    if p.exists():
        subprocess.Popen(["afplay", str(p)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _open_video(url: str | None) -> None:
    if not url:
        return
    subprocess.Popen(["open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _tool_bucket(tool: str) -> str:
    t = tool.lower()
    if any(x in t for x in ("write", "edit", "multiedit", "notebook")):
        return "Write"
    if "bash" in t:
        return "Bash"
    if any(x in t for x in ("read", "glob", "grep")):
        return "Read"
    if any(x in t for x in ("web", "search", "fetch")):
        return "Web"
    return "Other"


def handle(event: str, tool_name: str = "", notif_msg: str = "") -> None:
    cfg = _load_config()
    events = cfg.get("events", {})

    # Specific bucket takes priority over the generic event key.
    keys = [event]
    if event == "PreToolUse" and tool_name:
        keys.insert(0, f"PreToolUse_{_tool_bucket(tool_name)}")
    if event == "Notification" and "permission" in notif_msg.lower():
        keys.insert(0, "Notification_Permission")

    event_cfg: dict = {}
    for k in keys:
        if k in events:
            event_cfg = events[k]
            break

    if not event_cfg.get("enabled", True):
        return
    if random.random() > event_cfg.get("probability", 1.0):
        return

    messages = event_cfg.get("messages", [])
    if not messages:
        return

    title = event_cfg.get("title", "🏀 Curry Alert")
    body = random.choice(messages).replace("{tool}", tool_name).replace("{message}", notif_msg)

    sound = event_cfg.get("sound")
    video_url = event_cfg.get("video_url")

    _notify(title, body)
    _play_sound(None if video_url else sound)
    _open_video(video_url)


if __name__ == "__main__":
    handle(
        sys.argv[1] if len(sys.argv) > 1 else "Unknown",
        _tool_name,
        _notif_msg,
    )
