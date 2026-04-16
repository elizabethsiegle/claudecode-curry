# Desktop Curry — Demo Script

---

## THE HOOK  *(~30 seconds)*

> "Claude Code has a hooks system — shell commands that fire on events like tool use, prompts, and session end.
> 
> Most people use it for things like lint-on-save or running tests automatically.
>
> I used it to make Steph Curry narrate my entire coding session."

**[open curry.config.json in the editor]**

---

## WHAT IT IS  *(~45 seconds)*

> "This is Desktop Curry. It's a Steph Curry-themed notification system wired directly into Claude Code's lifecycle.
>
> Every time Claude does something — submits a prompt, runs a Bash command, asks for your permission, finishes a session — it fires a hook. That hook runs a Python script that pops a system notification, plays a sound, and can open a YouTube clip.
>
> The config here controls everything. Each event gets a title, a pool of random messages, a sound file, and an optional video URL. Probability lets you tune how often noisy events fire."

**[scroll through curry.config.json, point out events: UserPromptSubmit, PreToolUse_Bash, Stop]**

---

## LIVE DEMO  *(~2 minutes)*

> "Let me show it in action."

**[open Claude Code, start a session]**

**Submit a prompt:**
> "Watch the top right corner."

*— notification fires: "Chef Curry in the kitchen — cookin' something up 👨‍🍳"*

> "That's the UserPromptSubmit hook. Fires the instant you hit Enter."

**Ask Claude to run a Bash command:**
> "Now watch what happens when Claude uses the terminal."

*— notification fires: "Coast to coast — nothing can stop this man 💨"*

> "PreToolUse_Bash. Different hook, different message pool, different sound."

**Trigger a permission prompt:**
> "Here's my favorite one."

*— notification fires: "TIMEOUT called! Ref needs a word with you 🛑" + Basso sound*

> "That's the Notification_Permission event — when Claude Code needs your approval before doing something. The Night Night video opens too."

**End the session:**
> "And when Claude wraps up..."

*— notification fires: "Night Night. 🙏 *tucks in keyboard*" + Bang Bang video opens*

> "Bang Bang. Mike Breen. Only double-bang in history."

---

## HOW IT WORKS  *(~1 minute)*

> "Under the hood: install.py writes hooks directly into Claude Code's settings.json."

**[show the hooks block in ~/.claude/settings.json or run:]**
```bash
cat ~/.claude/settings.json | python3 -m json.tool | grep -A5 '"hooks"'
```

> "Each hook calls curry_alerts.py with the event name. The script reads the tool context from stdin, picks a random message, plays the sound with afplay, pops the notification with osascript, and opens the video if there is one.
>
> The clever part: it immediately forks a background process and the parent exits. Claude Code never waits. The alert is completely non-blocking."

**[show the detach pattern in curry_alerts.py briefly]**

---

## THE POINT  *(~30 seconds)*

> "This is a toy. But it's a toy that shows something real.
>
> Claude Code hooks are powerful. This is nine lines of config and a small Python script — but you could use the same pattern to post to Slack when a long task finishes, open a PR automatically, update a dashboard, trigger a deploy.
>
> Hooks turn Claude Code from a coding assistant into an orchestrator you can wire into anything.
>
> I just chose to wire it into Steph Curry."

---

## CUSTOMIZE / INSTALL  *(if time allows)*

```bash
# Install globally (all Claude Code sessions)
python3 install.py

# Install for one project only
python3 install.py --project

# Remove it
python3 install.py --uninstall
```

> "Edit curry.config.json to swap sounds, change messages, set probability to 0.1 if you want it to surprise you. The `sounds/` folder takes any .mp3 or .aiff."

---

## ONE-LINER CLOSER

> "Hooks are the API for your workflow. This one just happens to yell 'Night Night' when Claude is done."
