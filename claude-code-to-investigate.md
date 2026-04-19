# Claude Code — To Investigate

> Items from the viral cheat sheet that are unverified, custom, or need building.
> Work through each section to decide: confirm, discard, or build.

---

## Section 1: Unverified Slash Commands

These appeared on the cheat sheet but are NOT confirmed as native Claude Code commands.
They may exist in newer versions, be renamed, or be fabricated.

| Command | Claimed behavior | Status |
|---|---|---|
| `/resume` | Resume / switch session | Unverified |
| `/rename [name]` | Name current session | Unverified |
| `/branch [name]` | Branch conversation | Unverified |
| `/diff` | Interactive diff viewer | Unverified |
| `/copy [N]` | Copy last or Nth response | Unverified |
| `/rewind` | Rewind to a code checkpoint | Unverified |
| `/export` | Export conversation | Unverified |
| `/hooks` | Manage hooks | Unverified |
| `/agents` | Manage agents | Unverified |
| `/chrome` | Chrome integration | Unverified |
| `/power` | Unknown | Unverified |
| `/doctor` | Diagnose installation | Unverified |
| `/voice` | Push-to-talk input | Unverified |
| `/effort [level]` | Set effort: low/med/high/max/auto | Unverified |
| `/plan [desc]` | Enter plan mode + auto-start | Unverified |

**Action:** Test each one in a live session. If it works, move to confirmed sheet. If not, decide whether to build it as a custom skill.

---

## Section 2: Unverified Keyboard Shortcuts

These appeared on the cheat sheet but are not confirmed.

| Shortcut | Claimed behavior | Status |
|---|---|---|
| `Ctrl L` | Redraw screen | Unverified |
| `Ctrl O` | Toggle verbose/transcript | Unverified |
| `Ctrl G` | Open prompt in editor | Unverified |
| `Ctrl X E` | Open in editor (bash alias) | Unverified |
| `Ctrl B` | Background running task | Unverified |
| `Ctrl T` | Toggle task list | Unverified |
| `Ctrl V` | Paste image chip | Unverified |
| `Ctrl X K` | Kill background agents | Unverified |
| `Esc Esc` | Rewind or summarize | Unverified |
| `Alt P` | Switch model | Unverified |
| `Alt O` | Toggle fast mode | Unverified |
| `Up / Down` | Navigate sessions | Unverified |
| `Left / Right` | Expand / collapse | Unverified |

**Action:** Test in a live session. Note: some (Ctrl X E, Ctrl R) are standard bash terminal shortcuts that work in any terminal — not Claude-specific.

---

## Section 3: Custom Skills to Potentially Build

These were presented as native commands but are actually **custom skill files**.
They don't exist unless you build them. Decide which ones are worth building.

| Command | Claimed behavior | Status |
|---|---|---|
| `/simplify` | Code review with 3 parallel agents | Already exists (system skill) |
| `/batch` | Parallel changes across 5–30 worktrees | ✅ Built — `~/.claude/commands/batch.md` |
| `/debug [desc]` | Troubleshoot from a debug log | ✅ Built — `~/.claude/commands/debug.md` |
| `/btw [question]` | Side question with no context cost | ✅ Built — `~/.claude/commands/btw.md` |
| `/rc` / `/remote-control` | Bridge between Claude instances | ✅ Built — `~/.claude/commands/remote-control.md` (Slack-based) |
| `/doctor` | Diagnose Claude Code installation | ✅ Built — `~/.claude/commands/doctor.md` |
| `/voice` | Push-to-talk with space bar | ❌ Not feasible — requires OS audio hardware |
| `/autonomous` | Run tasks.md queue while away | ✅ Built — `~/.claude/commands/autonomous.md` (new, not on cheat sheet) |

**Note:** `/loop`, `/schedule`, `/claude-api` already exist as system skills.

---

## Section 4: Workflow Features to Verify

These were listed as workflow tips — some are plausible but unconfirmed.

| Feature | Claimed behavior | Status |
|---|---|---|
| `sparsePaths` | Checkout only needed dirs in worktree | Unverified |
| `claude -r "name"` | Resume session by name | Unverified |
| `Alt O` | Toggle fast mode | Unverified |
| `Ctrl O` | Toggle verbose mode | Unverified |
| `/permissions` → R | Retry a denied action | Unverified |
| `/voice` + Space bar | Record and send voice input | Unverified |

---

## How to Work Through This

1. **Test unverified commands** — open Claude Code, try each one, note what happens
2. **Mark confirmed ones** — move them to `claude-code-confirmed.md`
3. **Decide on custom builds** — for Section 3, pick the ones you'd actually use
4. **Build the chosen skills** — use `/new-project` or write the skill files manually

Start with whichever section is most useful to you.
