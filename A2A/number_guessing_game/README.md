# A2A Number-Guessing Demo (Python)

Sourced from the official A2A samples repo:
https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/number_guessing_game

This demo showcases three lightweight A2A agents that cooperate to play a
classic guess-the-number game.

Unlike a2a_server.py / a2a_client.py in the parent A2A/ folder, this demo
needs no LLM, no API keys, and no AWS credentials - it's pure Python game
logic wrapped in the real A2A protocol, so it's a good backup/bonus demo
if Bedrock access is acting up mid-class.

| Agent | Role |
|-------|------|
| **AgentAlice** | Picks a secret integer (1-100) and grades incoming guesses. |
| **AgentBob**   | CLI front-end - relays player guesses, shows Alice's hints, negotiates with Carol. |
| **AgentCarol** | Generates a text visualisation of the guess history and, on request, shuffles it until Bob is happy. |

## Before class: port check

Run this once before class. If it prints anything, kill it.

**Mac/Linux:**
```bash
lsof -i :8001 -i :8002 -i :8003
kill -9 <PID>
```

**Windows (bash):**
```bash
netstat -ano | grep -E ':(8001|8002|8003)'
# note the PID in the last column, then:
taskkill //PID <PID> //F
```

Nothing printed = ports are free, good to go.

## After class / after each rehearsal: cleanup

`Ctrl+C` in all three terminals, then re-run the port check above to
confirm they actually stopped.

## Setup

No separate setup needed. The repo-root `uv sync` from
[`PRE_CLASS_SETUP.md`](../../PRE_CLASS_SETUP.md) already installed
everything this demo requires (`a2a-sdk`, `uvicorn`, via the
`strands-agents[a2a]` extra). Don't create a separate venv for this folder.

## Running the demo

Open **three terminal tabs/windows** and paste the block below for that
agent into each. `uv run` finds the project environment automatically, so
there's no venv to activate — just `cd` and run. Do this in all three
terminals BEFORE class starts.

Terminal 1 - Alice (evaluator):
```bash
cd Projects/Building-Advanced-Agentic-Systems-on-AWS/A2A/number_guessing_game
uv run python agent_Alice.py
```

Terminal 2 - Carol (visualiser / shuffler):
```bash
cd Projects/Building-Advanced-Agentic-Systems-on-AWS/A2A/number_guessing_game
uv run python agent_Carol.py
```

Terminal 3 - Bob (CLI front-end - type guesses here):
```bash
cd Projects/Building-Advanced-Agentic-Systems-on-AWS/A2A/number_guessing_game
uv run python agent_Bob.py
```

Start Alice and Carol first (either order), then Bob last - Bob needs
both already running to talk to them.

Play in Bob's terminal - it will prompt you for numbers until Alice
replies with `correct! attempts: N`.

### If a command fails

- `ModuleNotFoundError: No module named 'a2a'` -> you ran
  `python agent_X.py` instead of `uv run python agent_X.py`. Plain `python`
  uses whatever interpreter is on your `PATH`, not this project's
  environment. If you're already using `uv run`, run `uv sync` from the
  repo root to (re)install dependencies.
- `can't open file '.../agent_X.py': No such file or directory` -> the
  `cd` line was skipped or run in the wrong terminal. Re-run the `cd`
  line first, then retry.
- Always run BOTH lines of the block together in each terminal, don't
  split them across separate steps.

During play, Bob repeatedly asks Carol to reshuffle the guess history
until it happens to come out sorted - a fun (if silly) way to exercise
multi-turn, task-referencing messages between agents. Good talking point:
this is NOT how you'd actually sort a list, it's deliberately inefficient
to force several round-trip A2A messages so you can watch the negotiation
happen live in the terminal logs.

## Directory layout

```text
number_guessing_game/
├── agent_Alice.py                  # Evaluator agent
├── agent_Bob.py                    # CLI front-end agent
├── agent_Carol.py                  # Visualiser / shuffler agent
├── utils/
│   ├── game_logic.py               # Pure game mechanics (transport-agnostic)
│   ├── helpers.py                  # Tiny generic helpers (JSON parsing, etc.)
│   ├── protocol_wrappers.py        # Convenience wrappers around A2A SDK
│   ├── server.py                   # Helper to spin up Starlette + SDK handler
│   └── __init__.py                 # Re-exports
├── config.py                       # Centralised port configuration
├── requirements.txt                # Upstream's dep list - kept for
│                                   #   reference/attribution. You do NOT
│                                   #   need to install it; the repo-root
│                                   #   pyproject.toml already covers these.
└── README.md                       # <- you are here
```

## Known limitations (from upstream)

- No streaming - the SDK returns "Unsupported operation" if attempted.
- Plain HTTP on localhost only - no TLS/auth. Fine for a demo, not for
  production.
