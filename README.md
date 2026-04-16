# desktop-curry

Steph Curry narrates your Claude Code sessions. Every prompt, tool call, permission prompt, and session end fires a macOS notification with a random Curry-inspired phrase and sound. On the big moments, a YouTube clip opens too. Works whenever Claude Code is running — glance at the notification center to know what he's doing.

## Prerequisites

- macOS (notifications via `osascript`, audio via `afplay`)
- Python 3.10+
- Claude Code

## Install

```bash
git clone https://github.com/elizabethsiegle/desktop-curry
python3 install.py
```

To scope it to a single project instead of all Claude Code sessions:

```bash
python3 install.py --project
```

## How it works

`install.py` writes hooks into `~/.claude/settings.json`. Each hook calls `curry_alerts.py` with the event name. The script reads tool context from stdin, picks a random message, plays a sound with `afplay`, fires a notification with `osascript`, and optionally opens a YouTube URL.

Every invocation forks a detached background process and exits immediately — Claude Code never waits.

## Session Events

```
      prompt               tool use            permission
   ~~~~~~~~~~~           ~~~~~~~~~~~          ~~~~~~~~~~~~~~
   ~ 🏀 Chef ~           ~ 🎯 Pull ~          ~ ⏱️ TIMEOUT ~
   ~ Curry  ~           ~ Up from ~          ~ Ref needs  ~
   ~ cooking ~           ~  logo   ~          ~ a word  🛑 ~
   ~~~~~~~~~~~           ~~~~~~~~~~~          ~~~~~~~~~~~~~~
```

| Event | Title | Default probability |
|---|---|---|
| `UserPromptSubmit` | 🏀 Chef Curry | 100% |
| `PreToolUse` (Write/Edit) | 🎯 Pulling Up | 100% |
| `PreToolUse` (Bash) | 💨 Fast Break | 100% |
| `PreToolUse` (Read/Glob/Grep) | 📼 Scouting | 40% |
| `PreToolUse` (Web) | 🔭 Googling | 50% |
| `PreToolUse` (other tools) | 🏀 Tool Time | 30% |
| `Notification` (permission) | ⏱️ TIMEOUT | 100% — opens Night Night clip |
| `Notification` (general) | 📣 Hey | 100% |
| `Stop` | 🙏 Night Night | 100% — opens Bang Bang clip |

## Customize

Edit `curry.config.json`. Every field is optional except `messages`:

```json
"Stop": {
  "enabled": true,
  "title": "🙏 Night Night",
  "messages": ["Night Night. 🙏", "Final buzzer. That's a wrap."],
  "sound": "sounds/buzzer.mp3",
  "video_url": "https://youtu.be/zrmivtWEAeo?t=3",
  "probability": 1.0
}
```

| Field | Default | Description |
|---|---|---|
| `enabled` | `true` | `false` silences the event entirely |
| `messages` | required | pool of strings — one picked at random each time |
| `sound` | `null` | `.mp3` or `.aiff` — relative paths resolve from this directory |
| `video_url` | `null` | URL opened in your default browser |
| `probability` | `1.0` | `0.0–1.0` chance the alert fires at all |

Drop custom audio into `sounds/` and reference it as `"sounds/filename.mp3"`.
System sounds work too: `"/System/Library/Sounds/Hero.aiff"`.

Messages support `{tool}` and `{message}` placeholders, substituted at runtime.

## Uninstall

```bash
python3 install.py --uninstall
```
