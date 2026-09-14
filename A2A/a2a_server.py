"""
Agent-to-Agent (A2A) protocol demo - SERVER side.

Consolidated from the "Creating an A2A Server" samples on:
https://strandsagents.com/docs/user-guide/concepts/multi-agent/agent-to-agent/

Unlike Workflow, Graph, Swarm, and Agents-as-Tools, A2A is NOT a
single-process pattern. Those patterns all wire multiple Agent objects
together inside one Python script. A2A is the opposite: it exposes an
agent over HTTP so a COMPLETELY SEPARATE process (potentially on a
different machine, written in a different language) can talk to it using
a standard protocol.

That's why this demo is two files instead of one:
  - a2a_server.py (this file)  - the "remote agent" from the diagram.
    Run this first and leave it running.
  - a2a_client.py               - the "local agent" from the diagram. Run
    this second, in a separate terminal, while the server is running.

RUN:
    Mac:     cd /Users/johnkrull/Projects/Strands/A2A
    Windows: cd /d/Projects/Strands/A2A
    uv run python a2a_server.py
It will block and serve requests until you Ctrl+C it.

NAMING NOTE: this folder cannot contain a file named a2a.py. The real A2A
protocol library is an installed package also called "a2a" (a2a-sdk). A
local a2a.py would shadow it and break imports like
"from a2a.server.agent_execution import ..." used by
strands.multiagent.a2a below.
"""

import logging
from strands import Agent
from strands.multiagent.a2a import A2AServer
from strands_tools.calculator import calculator

logging.basicConfig(level=logging.INFO)

# ADDED: BedrockModel import + pinned model. Without an explicit model,
# Agent() falls back to the SDK's built-in default model, which AWS has
# flagged "Legacy" and now rejects with ResourceNotFoundException. Same
# fix applied in workflow.py, graph.py, swarm.py, and tools.py.
from strands.models import BedrockModel

model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-5",
    region_name="us-east-1",
)


# A2A identifies each conversation by a context_id (roughly: one client
# session). agent_factory is called once per NEW context_id and the
# returned Agent is then reused for later requests in that same context -
# this is what gives two different callers separate conversation histories
# instead of bleeding into each other. This is the recommended mode over
# passing a single shared `agent=` (deprecated).
def create_agent(context_id: str) -> Agent:
    # ADDED: model=model (docs example omits it, same reason as above).
    return Agent(
        model=model,
        name="Calculator Agent",
        description="A calculator agent that can perform basic arithmetic operations.",
        tools=[calculator],
        callback_handler=None,
    )


# Everything the "Remote Agent" box in the diagram represents - the agent
# itself, the A2A server wrapping it, and the agent card - comes from this
# one A2AServer object. By default it:
#   - serves the agent card at /.well-known/agent-card.json (this is the
#     "Agent card" box in your diagram - metadata describing what this
#     agent is and what it can do, so a caller can discover it)
#   - handles A2A JSON-RPC requests at the root path
#   - listens on 127.0.0.1:9000 (host/port are configurable, shown below)
#   - supports streaming responses by default
a2a_server = A2AServer(agent_factory=create_agent, host="127.0.0.1", port=9000)

if __name__ == "__main__":
    # ADDED: this print + the __main__ guard. The docs snippet just calls
    # a2a_server.serve() at module level - added the guard and a status
    # message so it's clear (especially mid-demo) that the server is up
    # and where the agent card lives.
    print("Starting A2A server on http://127.0.0.1:9000")
    print("Agent card: http://127.0.0.1:9000/.well-known/agent-card.json")
    print("Leave this running, then run a2a_client.py in a separate terminal.")
    a2a_server.serve()
