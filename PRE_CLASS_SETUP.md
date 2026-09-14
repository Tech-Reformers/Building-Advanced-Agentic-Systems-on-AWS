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
3. [ ] Install the dependencies (`uv sync`)
4. [ ] Configure AWS Bedrock credentials
5. [ ] Run one demo to confirm everything works
6. [ ] (If doing the A2A number-guessing demo) run the port check

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

## 3. Install the dependencies

The repo root has a `pyproject.toml` listing everything the demos need, at
pinned versions. One command from the repo root installs all of it:

```bash
cd Projects/Building-Advanced-Agentic-Systems-on-AWS
uv sync
```

That creates `.venv/` at the repo root and installs the exact versions from
`uv.lock`. It's git-ignored, so everyone gets their own.

**You do NOT need to activate the venv.** All the demos are run with
`uv run python <file>.py`, and `uv run` finds this project's environment
automatically — even from a subfolder like `Workflow/`. That's why every
demo's `RUN:` block is just a `cd` plus a `uv run` line, with no `source
.../activate` step.

<details>
<summary>What got installed, and why</summary>

- `strands-agents[a2a]` — the base SDK, plus the `a2a-sdk` and `uvicorn`
  extras needed for `A2A/a2a_server.py` and `A2A/a2a_client.py`.
- `strands-agents-tools` — provides `calculator`, `current_time`, etc. used
  by `Cache/cache.py` and `A2A/a2a_server.py`.
- The `Memory/` demo uses `strands.memory` / `strands.vended_memory_stores`,
  which ship with the base `strands-agents` package — no extra install.
- The `A2A/number_guessing_game/` demo only needs `a2a-sdk` and `uvicorn`
  (covered by the `[a2a]` extra) — no LLM or AWS credentials for that one.

Versions are pinned exactly in `pyproject.toml` so a clone months from now
behaves the way it did in class. To move to newer versions on purpose, edit
those pins and re-run `uv sync`.
</details>

> **If you'd rather activate a venv the traditional way** (some editors and
> debuggers expect it), `uv sync` already created one — activate it with
> `source .venv/bin/activate` on Mac/Linux, or
> `source .venv/Scripts/activate` in Windows Git Bash. Note that on Windows
> `uv` prints the hint as `.venv\Scripts\activate` (the cmd.exe form) even
> in Git Bash; use forward slashes and `source` as shown.
>
> Avoid plain `pip install` in this repo. If you see
> `Defaulting to user installation because normal site-packages is not
> writeable` in an install log, packages went to your system Python instead
> of the venv — run `uv sync` and use `uv run` instead.

## 4. Configure AWS Bedrock credentials

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

## 5. Smoke test

Pick any demo and run it to confirm the dependencies + credentials work end
to end.

```bash
cd Projects/Building-Advanced-Agentic-Systems-on-AWS/Workflow
uv run python workflow.py
```

If it prints a research -> analysis -> report chain of output with no
`ResourceNotFoundException` or `AccessDeniedException`, you're set.

Each demo file's own `RUN:` docstring has the exact `cd` + run command -
see: `Workflow/workflow.py`, `Graph/graph.py`, `Swarm/swarm.py`,
`AgentAsTools/tools.py`, `State/state.py`, `Memory/memory.py`,
`Cache/cache.py`.

## 6. A2A demos - extra pre-class steps

There are two separate A2A demos:

- **`A2A/a2a_server.py` + `A2A/a2a_client.py`** - uses Bedrock, needs
  credentials from step 4. Run the server first (`uv run python
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

- **`ModuleNotFoundError: No module named 'strands'` (or `'a2a'`)** - most
  likely you ran `python file.py` instead of `uv run python file.py`. Plain
  `python` uses whatever interpreter is on your `PATH`, which isn't this
  project's environment unless you separately activated the venv. Use
  `uv run python <file>.py` and it works from any folder in the repo.

  If you ARE using `uv run` and still see this, re-run `uv sync` from the
  repo root — the environment may be missing or partially installed. And if
  an earlier plain `pip install` logged `Defaulting to user installation
  because normal site-packages is not writeable`, those packages went to
  your system Python; `uv sync` sorts it out.
- **`ResourceNotFoundException` on model invocation** - the pinned model
  ID (`us.anthropic.claude-sonnet-5`) is no longer active in your
  account/region. Run the `aws bedrock list-inference-profiles` command
  from step 4 and swap in a currently active model ID. Note it appears in
  every demo file (12 occurrences across the repo), so update all of them,
  not just the one you're running.
- **`AccessDeniedException`** - your AWS profile doesn't have Bedrock
  permissions, or `AWS_PROFILE`/`AWS_DEFAULT_REGION` aren't set in this
  terminal. Re-run step 4.
- **`UnicodeEncodeError` (e.g. `'charmap' codec can't encode character`)
  when `Workflow/workflow.py` or `Graph/graph.py` write `report.md`** -
  Windows-only. Python's default text-file encoding on Windows is the
  system codepage (e.g. `cp1252`), not UTF-8, so it can choke on
  characters the model outputs (smart quotes, em dashes, arrows, etc).
  Already fixed in this repo by opening `report.md` with
  `encoding="utf-8"` explicitly - if you see this on a fresh clone, make
  sure you have the latest version of these two files.
