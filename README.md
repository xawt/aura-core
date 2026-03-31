```diff
+ █████ L-CLI ████████████ AURA-CORE COMPUTER INTERFACE ████████████████████████████
```

# AURA-CORE

![Python](https://img.shields.io/badge/Python-3.12+-ffaf00?style=flat-square&labelColor=111111&color=ffaf00)
![OpenRouter](https://img.shields.io/badge/LLM-OpenRouter-6fa8dc?style=flat-square&labelColor=111111&color=6fa8dc)
![Textual](https://img.shields.io/badge/TUI-Textual-ffaf00?style=flat-square&labelColor=111111&color=ffaf00)
![Rich](https://img.shields.io/badge/CLI-Rich-6fa8dc?style=flat-square&labelColor=111111&color=6fa8dc)

**AURA-CORE** is a general-purpose AI agent built for learning and experimenting
with agentic systems. It runs a ReAct (Reason + Act) loop — the agent reasons
about a query, calls tools when needed, observes results, and iterates until it
produces a final answer.

Interfaces are styled after Star Trek LCARS — because why not.

---

## Architecture

```diff
+ main.py
+   └── Agent
+         ├── LLMClient        — OpenRouter API via OpenAI-compatible SDK
+         ├── Context          — conversation message history
+         ├── EventBus         — broadcasts tool calls, observations, answers
+         └── ToolRegistry     — pluggable tool system

  interfaces/cli/
    ├── interface.py           — TUI  (Textual, docked header + input)
    ├── handler.py             — TUI  event handler
    ├── rich_interface.py      — Rich scrolling CLI
    └── rich_handler.py        — Rich event handler
```

---

## Requirements

- Python `3.12+`
- [uv](https://github.com/astral-sh/uv) — package manager
- An [OpenRouter](https://openrouter.ai) API key

---

## Setup

```bash
git clone <repo>
cd aura-core

uv sync

cp .env.example .env
# OPENROUTER_API_KEY=sk-or-...
```

---

## Configuration

The default model is set in `config/default.yaml`:

```yaml
# config/default.yaml
model: google/gemini-2.0-flash-001
```

Any model available on OpenRouter can be used here, or switched at runtime
with `/model`.

---

## Running

```bash
uv run python main.py
```

### Selecting an interface

```diff
+ --ui tui    Full-screen Textual TUI — fixed header bar, docked input (default)
- --ui rich   Scrolling Rich CLI — LCARS-styled header printed inline
```

```bash
uv run python main.py             # TUI (default)
uv run python main.py --ui tui    # same
uv run python main.py --ui rich   # scrolling Rich CLI
```

---

## Commands

> Work in both interfaces.

| Command | Description |
|---|---|
| `/help` | Display command directory |
| `/model <name>` | Switch active model — e.g. `/model gpt-4o` |
| `/reset` | Purge conversation context |
| `/clear` | Clear the display |
| `/exit` | Terminate interface |

---

## Tools

| Tool | Description |
|---|---|
| `web_search` | Query the web via DuckDuckGo — invoked automatically by the agent |

---

## Stardate

The header displays a computed stardate:

```diff
+ SD = (year − 1987) × 1000 + (day_of_year / 365.25) × 1000
```

Based on the Star Trek: TNG convention — **1000 units = 1 year**.
