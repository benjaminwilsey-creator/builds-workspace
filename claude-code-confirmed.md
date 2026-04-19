# Claude Code — Confirmed Cheat Sheet

> Native features only. Verified against known Claude Code behavior.
> Last reviewed: 2026-04-18

---

## Slash Commands

### Session
| Command | What it does |
|---|---|
| `/clear` | Clear conversation history |
| `/compact [focus]` | Compress context, optional focus keyword |
| `/cost` | Show token usage + cache breakdown |
| `/context` | Show context window usage |
| `/help` | List available commands |
| `/version` | Show Claude Code version |

### Config
| Command | What it does |
|---|---|
| `/config` | Open settings |
| `/model [model]` | Switch the Claude model |
| `/fast [on\|off]` | Toggle fast output mode |
| `/permissions` | View or update tool permissions |
| `/keybindings` | Customize keyboard shortcuts |
| `/terminal-setup` | Configure terminal integration |
| `/theme` | Change color theme |

### Project
| Command | What it does |
|---|---|
| `/init` | Create a CLAUDE.md in current project |
| `/memory` | View or edit memory files |
| `/mcp` | List and manage MCP servers |

---

## Keyboard Shortcuts

### General Controls
| Shortcut | What it does |
|---|---|
| `Ctrl C` | Cancel current input or generation |
| `Ctrl D` | Exit Claude Code session |
| `Ctrl R` | Reverse search through input history |
| `Shift Tab` | Cycle through permission modes |
| `Alt T` | Toggle thinking (extended reasoning) on/off |

### Input
| Shortcut | What it does |
|---|---|
| `\Enter` or `Ctrl J` | Insert newline (multiline input) |
| `/` | Open slash command menu |
| `!` | Prefix for direct bash command |
| `@` | File mention + autocomplete |

---

## CLI Flags (Terminal)

### Starting a Session
```bash
claude                          # Start interactive session
claude -c                       # Continue last conversation
claude -p "your question"       # Non-interactive, single query
cat file.txt | claude -p "..."  # Pipe file contents as input
```

### Output & Cost Control
```bash
--output-format json            # Structured JSON output
--output-format stream-json     # Streaming JSON
--max-budget-usd 5              # Hard cost cap ($5 example)
```

### Permissions & Mode
```bash
--permission-mode plan          # Start in plan mode (read-only by default)
--permission-mode auto-accept   # Auto-approve all tool calls
```

### Worktrees (Isolated Environments)
```bash
--worktree name                 # Run in an isolated git worktree
```

---

## Power Tips (Confirmed)

| Tip | How it works |
|---|---|
| **ultrathink** | Type the word `ultrathink` in your prompt to trigger maximum extended thinking |
| **Auto-compact** | Claude automatically compacts context at ~95% capacity |
| **CLAUDE.md survives compaction** | Your project instructions are re-injected after compaction |
| **1M context window** | Available on Opus 4.6 with Max, Team, or Enterprise plans |
| **Pipe input** | `cat file \| claude -p "prompt"` — great for processing files non-interactively |

---

## Permission Modes (Shift Tab to cycle)

| Mode | Behavior |
|---|---|
| `auto-accept` | Claude approves all tool calls automatically |
| `plan` | Claude plans only — no writes or executions without approval |
| `default` | Claude asks before each tool call |
