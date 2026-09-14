# Pre-Class Setup

> **Class:** Strands Agents demos - Workflow, Graph, Swarm, Agents-as-Tools, State,
> Memory, Prompt Caching, and Agent-to-Agent (A2A).
>
> **Do this BEFORE class starts.** Nothing here requires the instructor, and
> most of it (steps 1-4) only needs to be done once per machine.
>
> For a tour of what each demo folder teaches, see [`README.md`](README.md).

## Pre-class checklist

1. [ ] Clone/pull the repo
2. [ ] Install `uv`
3. [ ] Create the shared virtual environment
4. [ ] Install dependencies into it
5. [ ] Configure AWS Bedrock credentials
6. [ ] Run one demo to confirm everything works
7. [ ] (If doing the A2A number-guessing demo) run the port check

---

## 1. Clone / pull the repo

Mac/Linux and Windows Git Bash use the same commands - Git Bash gives
Windows the same Unix-style paths as a Mac Terminal. Pick any folder
you like to keep your projects in (this just uses `~/Projects` as an
example - substitute wherever you keep your code):

```bash
cd ~/Projects
git clone https://github.com/Tech-Reformers/Building-Advanced-Agentic-Systems-on-AWS.git
cd Building-Advanced-Agentic-Systems-on-AWS
```

If you already have it cloned, just `git pull` instead.

All later steps in this guide assume you're running commands from
inside this repo folder (referred to as "the repo root") - no need to
track the full path, just `cd` there once per terminal session.

## 2. Install `uv`

Check if you already have it:
```bash
uv --version
```

If not installed, see the [official installation guide](https://docs.astral.sh/uv/getting-started/installation/):

**Mac/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell - run once, outside bash):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Then close and reopen your Git Bash terminal so `uv` is on your `PATH`.

## 3. Create the shared virtual environment

All the top-level demo folders (`Workflow`, `Graph`, `Swarm`, `AgentAsTools`,
`State`, `Memory`, `Cache`, `A2A`) share ONE `.venv` at the repo root.
Create it once from the repo root:

```bash
cd Projects/Building-Advanced-Agentic-Systems-on-AWS
uv venv
```

This creates `.venv/` at the repo root (it's git-ignored, so everyone
creates their own).

> **Windows note:** `uv venv` prints an activation hint like
> `Activate with: .venv\Scripts\activate` - that's the cmd.exe/PowerShell
> form and always shows that way on Windows, even in Git Bash. In Git Bash,
> use forward slashes and `source` instead (see step 4 below):
> `source .venv/Scripts/activate`

## 4. Install dependencies

With the venv created, install everything the demos need. Use `uv pip
install` (not plain `pip install`) - `uv venv` creates a minimal venv
without `pip` seeded into it, so a plain `pip install` command can fall
through to whatever `pip` is on your system `PATH` and install into your
system/user Python instead of the venv. `uv pip install` always targets
the active venv correctly.

**Mac/Linux:**
```bash
source .venv/bin/activate
uv pip install 'strands-agents[a2a]' strands-agents-tools
```

**Windows (Git Bash):**
```bash
source .venv/Scripts/activate
uv pip install 'strands-agents[a2a]' strands-agents-tools
```

> **If you already ran plain `pip install` and still get
> `ModuleNotFoundError: No module named 'strands'`:** check the install
> output for a line like `Defaulting to user installation because normal
> site-packages is not writeable` - that means it installed outside the
> venv. Re-run the `uv pip install` command above instead.

- `strands-agents[a2a]` pulls in the base SDK plus the `a2a-sdk` and
  `uvicorn` extras needed for `A2A/a2a_server.py` and `A2A/a2a_client.py`.
- `strands-agents-tools` provides `calculator`, `current_time`, etc. used
  by `Cache/cache.py` and `A2A/a2a_server.py`.
- The `Memory/` demo uses `strands.memory` / `strands.vended_memory_stores`,
  which ship with the base `strands-agents` package - no extra install.
- The `A2A/number_guessing_game/` demo is self-contained and only needs
  `a2a-sdk` and `uvicorn` (already covered above by the `[a2a]` extra) -
  no LLM or AWS credentials required for that one.

You should NOT need to `deactivate`/reactivate between demos - each demo's
`RUN:` comment includes the `cd` + you already have the venv active for
the rest of the session. Just re-`source` the activate line in any new
terminal tab.

## 5. Configure AWS Bedrock credentials

Every demo except `Memory/` (partially) and `A2A/number_guessing_game/`
calls Amazon Bedrock, so you need working AWS credentials with Bedrock
access before class.

**Mac and Windows (Git Bash):**
```bash
aws sso login --profile your-profile
export AWS_PROFILE=your-profile
export AWS_DEFAULT_REGION=us-east-1
```

Verify Bedrock access and confirm the model ID used in the demos is
still active:
```bash
aws bedrock list-inference-profiles --region us-east-1
```
All demos are pinned to `us.anthropic.claude-sonnet-5` in `us-east-1`. If
that model shows as inactive/legacy in your account, update the
`model_id` in each demo file before class.

## 6. Smoke test

Pick any demo and run it to confirm the venv + credentials work end to end.

```bash
cd Projects/Building-Advanced-Agentic-Systems-on-AWS/Workflow
uv run python workflow.py
```

If it prints a research -> analysis -> report chain of output with no
`ResourceNotFoundException` or `AccessDeniedException`, you're set.

Each demo file's own `RUN:` docstring has the exact `cd` + run command for
both Mac and Windows - see:
`Workflow/workflow.py`, `Graph/graph.py`, `Swarm/swarm.py`,
`AgentAsTools/tools.py`, `State/state.py`, `Memory/memory.py`,
`Cache/cache.py`.

## 7. A2A demos - extra pre-class steps

There are two separate A2A demos:

- **`A2A/a2a_server.py` + `A2A/a2a_client.py`** - uses Bedrock, needs
  credentials from step 5. Run the server first (`uv run python
  a2a_server.py`), then the client in a second terminal.
- **`A2A/number_guessing_game/`** - no LLM, no AWS needed, but runs THREE
  processes on fixed ports (8001-8003). Run the port check below before
  class and see `A2A/number_guessing_game/README.md` for full run
  instructions (Mac and Windows commands included there too).

**Port check - Mac/Linux:**
```bash
lsof -i :8001 -i :8002 -i :8003
kill -9 <PID>   # only if something printed
```

**Port check - Windows (Git Bash):**
```bash
netstat -ano | grep -E ':(8001|8002|8003)'
taskkill //PID <PID> //F   # only if something printed
```

## Troubleshooting

- **`ModuleNotFoundError: No module named 'strands'`** - two possible
  causes:
  1. The venv isn't activated. Re-run the `source .venv/bin/activate`
     (Mac) or `source .venv/Scripts/activate` (Windows) line from step 4.
  2. Dependencies were installed with plain `pip install` instead of
     `uv pip install`, and landed outside the venv (look for "Defaulting
     to user installation" in the install log). Re-run step 4 using
     `uv pip install`.
- **`ResourceNotFoundException` on model invocation** - the pinned model
  ID (`us.anthropic.claude-sonnet-5`) is no longer active in your
  account/region. Run the `aws bedrock list-inference-profiles` command
  from step 5 and swap in a currently active model ID.
- **`AccessDeniedException`** - your AWS profile doesn't have Bedrock
  permissions, or `AWS_PROFILE`/`AWS_DEFAULT_REGION` aren't set in this
  terminal. Re-run step 5.
- **`ModuleNotFoundError: No module named 'a2a'`** - either the venv
  wasn't activated, or `strands-agents[a2a]` wasn't installed (see step 4).
- **`UnicodeEncodeError` (e.g. `'charmap' codec can't encode character`)
  when `Workflow/workflow.py` or `Graph/graph.py` write `report.md`** -
  Windows-only. Python's default text-file encoding on Windows is the
  system codepage (e.g. `cp1252`), not UTF-8, so it can choke on
  characters the model outputs (smart quotes, em dashes, arrows, etc).
  Already fixed in this repo by opening `report.md` with
  `encoding="utf-8"` explicitly - if you see this on a fresh clone, make
  sure you have the latest version of these two files.
