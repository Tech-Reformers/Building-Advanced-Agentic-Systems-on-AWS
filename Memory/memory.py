"""
Memory demo.

Consolidated from the code samples on:
https://strandsagents.com/docs/user-guide/concepts/memory/overview/

RUN:
    Mac:     cd /Users/johnkrull/Projects/Building-Advanced-Agentic-Systems-on-AWS/Memory
    Windows: cd /d/Projects/Building-Advanced-Agentic-Systems-on-AWS/Memory
    uv run python memory.py

One process, one terminal. For the "it remembers across restarts" payoff,
run it TWICE (two separate commands, not two calls in one run) and ask
about the preference the second time.

TO SEE THE ACTUAL SAVED MEMORY: this demo never prints the memory file
itself - the agent only confirms verbally that it remembered. To show the
class the real file on disk, open another terminal and run:
    cat ~/.strands/memory/notes.json
(full path - Mac:     /Users/johnkrull/.strands/memory/notes.json)
(full path - Windows: /c/Users/JohnKrull/.strands/memory/notes.json)

Pattern: by default a Strands agent starts every conversation from zero -
no memory of past sessions. A MemoryManager gives an agent long-term
memory that persists ACROSS RESTARTS, backed by a "store" (here, the
zero-setup TestMemoryStore, which just writes to a local JSON file).

The manager handles three jobs once a store is attached:
  - Recall:    the agent can search stored memories on demand via a tool
  - Injection: relevant memories get folded into the prompt automatically,
               before the model even runs - no tool call needed
  - Extraction: turning conversation messages into memories (opt-in, not
               used in this demo - see the docs for BedrockKnowledgeBaseStore)

Recall and injection are ON by default once you attach a store. Writing
(the agent saving new memories itself) is opt-in via add_tool_config.
"""

import logging
from strands import Agent
from strands.models import BedrockModel
from strands.memory import MemoryManager
from strands.vended_memory_stores.test_memory_store import TestMemoryStore

# ADDED: BedrockModel import + pinned model. Without an explicit model,
# Agent() falls back to the SDK's built-in default model, which AWS has
# flagged "Legacy" and now rejects with ResourceNotFoundException. Same
# fix applied in workflow.py, graph.py, swarm.py, and tools.py.
# Verify active models for your account/region with:
#   aws bedrock list-inference-profiles --region us-east-1
model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-5",
    region_name="us-east-1",
)

# Enable debug logs so students can see the manager searching memory and
# injecting results into the prompt, same convention used in the other
# demo files in this project.
logging.getLogger("strands").setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

# TestMemoryStore needs no cloud account and persists to disk by default -
# this is the "zero-setup" store from the docs, good for a demo since
# there's no Bedrock Knowledge Base to provision.
# ADDED: persist=True is actually the default, made explicit here so it's
# obvious in the demo that this file writes to disk and will remember
# things the NEXT time you run it, not just within one run.
# Default location: ~/.strands/memory/notes.json
store = TestMemoryStore(name="notes", persist=True)

# ADDED: model=model (docs example omits it, same reason as above).
# add_tool_config=True is opt-in per the docs - without it, the agent can
# only ever READ memories (recall + injection), never save new ones. We
# turn it on here so this demo shows the full read+write picture in one
# file: the agent can decide for itself when something is worth
# remembering, by calling the add_memory tool.
# ADDED: callback_handler=None. Without it, the Agent's default handler
# streams its response to stdout live as it generates - then our own
# print(result) below prints the same finished text again, so you'd see
# every answer twice. Setting it to None means our print() calls are the
# only thing writing output, same convention used in workflow.py/tools.py.
agent = Agent(
    model=model,
    system_prompt=(
        "You are a helpful assistant with long-term memory. "
        "When the user tells you a preference or fact worth remembering "
        "for future conversations, use the add_memory tool to save it."
    ),
    memory_manager=MemoryManager(
        stores=[store],
        add_tool_config=True,
    ),
    callback_handler=None,
)

# ADDED: entry point. The docs page shows isolated snippets (create a
# store, attach a manager, configure tools) meant to be dropped into a
# larger project - this assembles them into one runnable script.
if __name__ == "__main__":
    print("Memory demo - notes persist to ~/.strands/memory/notes.json")
    print("Run this script once to teach it something, then run it AGAIN")
    print("(a fresh process) and ask about it - it will still remember.\n")

    # This single call demonstrates both write and read in one turn:
    # the agent should recognize the stated preference, call add_memory
    # to save it, and confirm back to you that it remembered.
    result = agent(
        "Please remember that I prefer window seats when flying, "
        "and that my favorite programming language is Python."
    )
    print(f"\n{result}")

    print("\n--- Now asking a follow-up in the SAME run ---")
    # Within the same run, this demonstrates injection: the manager
    # searches memory before this call and folds matching entries into
    # the prompt automatically - no add_memory or search tool call
    # required for the agent to "remember" what was just said.
    result2 = agent("What kind of seat do I prefer when flying?")
    print(f"\n{result2}")
