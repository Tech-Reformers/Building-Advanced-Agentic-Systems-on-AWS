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

No separate setup needed. This project's main `.venv` already has
everything required (`a2a-sdk`, `uvicorn`) installed via
`pip install 'strands-agents[a2a]'`. Use that same venv for all three
agents below - do not create a new one.

- Mac:     `/Users/johnkrull/Projects/Strands/.venv`
- Windows: `/d/Projects/Strands/.venv`

## Running the demo

Open **three terminal tabs/windows**. In EACH one, paste the full block
below for that agent - each block includes `cd` + activating the venv, so
it works no matter what directory the terminal starts in. Do this setup
in all three terminals BEFORE class starts.

**Mac/Linux:**

Terminal 1 - Alice (evaluator):
```bash
cd /Users/johnkrull/Projects/Strands/A2A/number_guessing_game
source /Users/johnkrull/Projects/Strands/.venv/bin/activate
python agent_Alice.py
```

Terminal 2 - Carol (visualiser / shuffler):
```bash
cd /Users/johnkrull/Projects/Strands/A2A/number_guessing_game
source /Users/johnkrull/Projects/Strands/.venv/bin/activate
python agent_Carol.py
```

Terminal 3 - Bob (CLI front-end - type guesses here):
```bash
cd /Users/johnkrull/Projects/Strands/A2A/number_guessing_game
source /Users/johnkrull/Projects/Strands/.venv/bin/activate
python agent_Bob.py
```

**Windows (bash):**

Terminal 1 - Alice (evaluator):
```bash
cd /d/Projects/Strands/A2A/number_guessing_game
source /d/Projects/Strands/.venv/Scripts/activate
python agent_Alice.py
```

Terminal 2 - Carol (visualiser / shuffler):
```bash
cd /d/Projects/Strands/A2A/number_guessing_game
source /d/Projects/Strands/.venv/Scripts/activate
python agent_Carol.py
```

Terminal 3 - Bob (CLI front-end - type guesses here):
```bash
cd /d/Projects/Strands/A2A/number_guessing_game
source /d/Projects/Strands/.venv/Scripts/activate
python agent_Bob.py
```

Start Alice and Carol first (either order), then Bob last - Bob needs
both already running to talk to them.

Play in Bob's terminal - it will prompt you for numbers until Alice
replies with `correct! attempts: N`.

### If a command fails

- `ModuleNotFoundError: No module named 'a2a'` -> the venv wasn't
  activated, or a different `python`/`python3` is being used. Re-run the
  `source .../activate` line and confirm the prompt shows `(.venv)` at
  the start before running `python agent_X.py` again.
- `can't open file '.../agent_X.py': No such file or directory` -> the
  `cd` line was skipped or run in the wrong terminal. Re-run the `cd`
  line first, then retry.
- Always run the FULL three-line block together in each terminal, don't
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
├── requirements.txt                # Runtime deps
└── README.md                       # <- you are here
```

## Known limitations (from upstream)

- No streaming - the SDK returns "Unsupported operation" if attempted.
- Plain HTTP on localhost only - no TLS/auth. Fine for a demo, not for
  production.
