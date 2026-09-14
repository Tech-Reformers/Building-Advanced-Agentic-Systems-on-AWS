# Strands Agents Class Demos

A set of runnable, commented example scripts built for teaching the [Strands Agents SDK](https://strandsagents.com/) — a model-driven, open-source Python/TypeScript framework for building AI agents. See the official [Get Started guide](https://strandsagents.com/docs/user-guide/quickstart/overview/) for the SDK's own quickstart.

Every demo in this repo is adapted from a real code sample on the [Strands documentation site](https://strandsagents.com/docs/), extended into a complete, runnable script, and commented to explain exactly what was added or changed and why. Where a comment starts with `# ADDED:`, `# CHANGED FROM DOCS:`, or `# REMOVED:`, that's a deliberate deviation from the docs sample, explained in place — the comment is the lesson.

## Who this is for

Students following along with a Strands Agents class, or anyone who wants working, end-to-end examples of each multi-agent pattern the SDK supports, rather than isolated code snippets.

## Prerequisites

- Python 3.10+ (this repo was built and tested on Python 3.14)
- [uv](https://docs.astral.sh/uv/) for running scripts (`uv run python <file>.py`), or a plain virtualenv with `pip install strands-agents`
- An AWS account with access to Amazon Bedrock, and AWS credentials configured (`aws configure`, `aws sso login`, or environment variables)
- Model access enabled for the Bedrock model used in these demos (`us.anthropic.claude-sonnet-5`) in your AWS account/region — check the Bedrock console's Model access page if you hit an access-denied error

Every demo explicitly pins its model with a `BedrockModel(model_id=..., region_name=...)` instead of relying on the SDK's default model. AWS periodically marks older model versions "Legacy," which makes them stop working with no code change on your end — pinning an active model avoids that. Verify which models are currently active in your account/region with:
```bash
aws bedrock list-inference-profiles --region us-east-1
```

## Setup

**See [`PRE_CLASS_SETUP.md`](PRE_CLASS_SETUP.md) for the full step-by-step checklist**, with separate Mac and Windows (Git Bash) commands for every step, plus troubleshooting for the errors people actually hit (missing `strands` module, wrong venv, Bedrock access, Windows-only encoding issues, etc).

A note on paths: every demo's `RUN:` block and this repo's setup docs use `Projects/Building-Advanced-Agentic-Systems-on-AWS/...` as the example path. Swap in wherever you actually cloned the repo. Mac/Linux and Windows Git Bash use the same forward-slash `cd` commands throughout — Git Bash gives Windows the same Unix-style paths as a Mac Terminal, so there's no separate Windows path syntax to learn (the only real Mac/Windows difference in this repo is the venv's internal layout, `bin/activate` vs `Scripts/activate`, called out where it matters).

Quick version, if you already know what you're doing:
```bash
git clone https://github.com/Tech-Reformers/Building-Advanced-Agentic-Systems-on-AWS.git
cd Building-Advanced-Agentic-Systems-on-AWS
uv venv
source .venv/bin/activate       # Mac/Linux
source .venv/Scripts/activate   # Windows (Git Bash)
uv pip install 'strands-agents[a2a]' strands-agents-tools
```

Each demo file's docstring has a `RUN:` block at the top with the exact commands to run it (Mac and Windows) — open the file first, run what it says.

## Demos

| Folder | Concept | Docs page |
|---|---|---|
| [`Workflow/`](Workflow/workflow.py) | Sequential multi-agent pipelines — fixed order, each agent's output feeds the next | [Workflow](https://strandsagents.com/docs/user-guide/concepts/multi-agent/workflow/) |
| [`Graph/`](Graph/graph.py) | Dependency-graph multi-agent orchestration — parallel branches, join points | [Graph](https://strandsagents.com/docs/user-guide/concepts/multi-agent/graph/) |
| [`Swarm/`](Swarm/swarm.py) | Self-organizing multi-agent handoffs — agents decide who goes next | [Swarm](https://strandsagents.com/docs/user-guide/concepts/multi-agent/swarm/) |
| [`AgentAsTools/`](AgentAsTools/tools.py) | Wrapping specialist agents as tools for an orchestrator agent | [Agents as Tools](https://strandsagents.com/docs/user-guide/concepts/multi-agent/agents-as-tools/) |
| [`A2A/`](A2A/) | Agent-to-Agent protocol — a local agent talking to a remote agent over HTTP, plus a fun 3-agent number-guessing sample from Google's official A2A samples repo | [Agent-to-Agent (A2A) Protocol](https://strandsagents.com/docs/user-guide/concepts/multi-agent/agent-to-agent/) |
| [`Memory/`](Memory/memory.py) | Long-term memory that persists across sessions (recall, injection, and agent-driven writes) | [Memory](https://strandsagents.com/docs/user-guide/concepts/memory/overview/) |
| [`State/`](State/state.py) | The three kinds of agent state: conversation history, agent state, and invocation state | [State Management](https://strandsagents.com/docs/user-guide/concepts/agents/state/) |
| [`Cache/`](Cache/cache.py) | Bedrock prompt caching — system prompt, tool, and automatic multi-turn caching, with cache hit/miss token metrics | [Amazon Bedrock](https://strandsagents.com/docs/user-guide/concepts/model-providers/amazon-bedrock/) |
| [`my_agent.py`](my_agent.py) | A minimal single-agent example with custom tools, for a first "hello world" run | [Quickstart](https://strandsagents.com/docs/user-guide/quickstart/overview/) |
| [`my_strands_agent/`](my_strands_agent/) | A `uv`-managed standalone project version of the single-agent quickstart | [Python Quickstart](https://strandsagents.com/docs/user-guide/quickstart/python/) |

### A2A/number_guessing_game

Worth a special mention: this is the one demo in the repo that runs with **no AWS account, no API keys, and no Bedrock calls at all** — three agents (Alice, Bob, Carol) play a number-guessing game using the real A2A protocol, pure Python logic underneath. It's a good first thing to try if you're still setting up AWS credentials, or a reliable backup demo if Bedrock access is acting up. See its own [README](A2A/number_guessing_game/README.md) for setup, including pre/post-class port cleanup steps.

## A note on the AI-agent-generated origin of this repo

These demos were built interactively with an AI coding assistant, working directly from the Strands documentation samples linked above. Where a demo deviates from the docs (a missing entry point, a stale default model, a naming collision, a double-printed response), that's a real bug that was actually hit and fixed while building this repo — the comments explaining those fixes are left in intentionally, as a teaching aid. If you're a student reading this: those comments are worth reading closely. They're the difference between "code that looks right" and "code that actually runs."

## License

Educational use for the class this repo was built for. Adapted code samples originate from the [Strands Agents documentation](https://strandsagents.com/) (Apache 2.0) and, for `A2A/number_guessing_game`, from the [a2aproject/a2a-samples](https://github.com/a2aproject/a2a-samples) repository.
