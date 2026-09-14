"""
Agent-to-Agent (A2A) protocol demo - CLIENT side.

Consolidated from the "Consuming Remote Agents" samples on:
https://strandsagents.com/docs/user-guide/concepts/multi-agent/agent-to-agent/

This is the "Local Agent" / "A2A client" box from the diagram. It does NOT
create the Calculator Agent itself - it connects to the already-running
A2A server (a2a_server.py) over HTTP and talks to it using the A2A
protocol. A2AAgent is what makes that feel like calling a normal Strands
Agent, even though the actual agent is running in a different process.

SETUP - run in this order, in two separate terminals:
  cd Projects/Building-Advanced-Agentic-Systems-on-AWS/A2A   (both terminals)

  1. uv run python a2a_server.py     (start this first, leave it running)
  2. uv run python a2a_client.py     (then run this)

NAMING NOTE: this file cannot be named a2a.py. The real A2A protocol
library is an installed package also called "a2a" (a2a-sdk). If a script
in this folder is named a2a.py, Python's import system finds that local
file before the installed package, and any code importing "a2a" (like
strands.multiagent.a2a, used by a2a_server.py) breaks with
"ModuleNotFoundError: No module named 'a2a.client'; 'a2a' is not a
package". Keep both files named something other than a2a.py.
"""

import asyncio
from strands.agent.a2a_agent import A2AAgent

# ADDED: entry point + everything below. The docs page shows several
# separate snippets (basic invoke, fetching the agent card, async
# invocation) as independent examples - this consolidates them into one
# runnable script so a single "uv run python a2a.py" demonstrates all
# three in sequence.


async def main() -> None:
    # A2AAgent wraps the A2A protocol communication (resolving the agent
    # card, configuring the HTTP client, building/parsing protocol
    # messages) behind an interface that looks just like a local Agent.
    # endpoint is the ONLY required argument - it's the base URL where
    # a2a_server.py is listening.
    a2a_agent = A2AAgent(endpoint="http://127.0.0.1:9000")

    # get_agent_card() fetches the remote agent's metadata - this is the
    # "Agent card" box in the diagram. It's how a caller can discover
    # what a remote agent is called and what it's capable of, without
    # already knowing anything about its implementation.
    card = await a2a_agent.get_agent_card()
    print(f"Connected to remote agent: {card.name}")
    print(f"Description: {card.description}")
    print(f"Skills: {card.skills}\n")

    # Invoking an A2AAgent looks identical to invoking a local Agent, but
    # under the hood this sends a JSON-RPC request over HTTP to
    # a2a_server.py, which runs it through the real Calculator Agent and
    # streams the result back. Strands calls this the "Artifact" flowing
    # back to the local agent in the diagram.
    result = await a2a_agent.invoke_async("What is 10 to the power of 6?")

    # Unpacking that response, one step at a time - this chain of lookups
    # is doing more than it looks like:
    #   result.message      -> a message dict, same shape as the entries in
    #                          agent.messages (see the State demo)
    #   ['content']         -> a LIST of content blocks, not a single value.
    #                          A message can carry several blocks: text,
    #                          toolUse, toolResult, images.
    #   [0]                 -> the first block. Fine here because we know
    #                          this reply is a single text block.
    #   ['text']            -> the actual string.
    #
    # Be aware this is brittle by design for demo brevity: if the remote
    # agent ever replies with a non-text block first (a tool call, say),
    # [0]['text'] raises KeyError. Production code should look for the text
    # block instead of assuming position 0 - something like:
    #   text = next(b["text"] for b in result.message["content"] if "text" in b)
    print(f"Result: {result.message['content'][0]['text']}")


if __name__ == "__main__":
    asyncio.run(main())
