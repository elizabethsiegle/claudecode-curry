#!/usr/bin/env python3
import sys
import json
import shutil
from pathlib import Path

SCRIPT_PATH = Path(__file__).parent.resolve() / "curry_alerts.py"


def _cmd(event: str) -> str:
    return f"{sys.executable} {SCRIPT_PATH} {event}"


CURRY_HOOKS = {
    "UserPromptSubmit": [
        {"hooks": [{"type": "command", "command": _cmd("UserPromptSubmit")}]},
    ],
    "PreToolUse": [
        {"matcher": "Write|Edit|MultiEdit|NotebookEdit", "hooks": [{"type": "command", "command": _cmd("PreToolUse")}]},
        {"matcher": "Bash",                              "hooks": [{"type": "command", "command": _cmd("PreToolUse")}]},
        {"matcher": "Read|Glob|Grep",                    "hooks": [{"type": "command", "command": _cmd("PreToolUse")}]},
        {"matcher": "WebSearch|WebFetch",                "hooks": [{"type": "command", "command": _cmd("PreToolUse")}]},
    ],
    "Notification": [
        {"hooks": [{"type": "command", "command": _cmd("Notification")}]},
    ],
    "Stop": [
        {"hooks": [{"type": "command", "command": _cmd("Stop")}]},
    ],
}


def _load(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError:
            print(f"⚠️  {path} has invalid JSON — backing up and starting fresh.")
            shutil.copy(path, path.with_suffix(".bak.json"))
    return {}


def _save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def _is_curry(cmd: str) -> bool:
    return "curry_alerts.py" in cmd


def install(settings_path: Path) -> None:
    cfg = _load(settings_path)
    hooks = cfg.setdefault("hooks", {})
    added = 0

    for event, new_entries in CURRY_HOOKS.items():
        bucket = hooks.setdefault(event, [])
        before = len(bucket)
        bucket[:] = [e for e in bucket if not any(_is_curry(h.get("command", "")) for h in e.get("hooks", []))]
        if (removed := before - len(bucket)):
            print(f"  ↺  Replaced {removed} existing Curry hook(s) for {event}")
        bucket.extend(new_entries)
        added += len(new_entries)

    _save(settings_path, cfg)
    print(f"\n✅  Installed {added} hook entries → {settings_path}")
    print(f"    Script: {SCRIPT_PATH}")
    print("\n🏀  Curry Alerts is live. Start a Claude Code session to test it.")
    print("    Customize messages / sounds / videos in curry.config.json\n")


def uninstall(settings_path: Path) -> None:
    if not settings_path.exists():
        print(f"Nothing to uninstall — {settings_path} doesn't exist.")
        return

    cfg = _load(settings_path)
    hooks = cfg.get("hooks", {})
    total = 0

    for event in list(hooks.keys()):
        before = len(hooks[event])
        hooks[event] = [e for e in hooks[event] if not any(_is_curry(h.get("command", "")) for h in e.get("hooks", []))]
        total += before - len(hooks[event])
        if not hooks[event]:
            del hooks[event]

    _save(settings_path, cfg)
    print(f"🗑️   Removed {total} Curry hook entries from {settings_path}")


def main() -> None:
    args = sys.argv[1:]
    project = "--project" in args
    removing = "--uninstall" in args

    if project:
        target = Path(".claude") / "settings.json"
        scope = "project"
    else:
        target = Path.home() / ".claude" / "settings.json"
        scope = "global"

    print(f"{'Uninstalling' if removing else 'Installing'} Curry Alerts ({scope}) → {target}\n")
    if removing:
        uninstall(target)
    else:
        install(target)


if __name__ == "__main__":
    main()
