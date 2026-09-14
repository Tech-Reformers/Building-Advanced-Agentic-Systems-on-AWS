"""
Swarm demo.

Consolidated from the code samples on:
https://strandsagents.com/docs/user-guide/concepts/multi-agent/swarm/

RUN:
    cd Projects/Building-Advanced-Agentic-Systems-on-AWS/Swarm
    uv run python swarm.py

One process, one terminal. No fixed order - agents call the handoff_to_agent
tool to pass control to whichever agent they think should go next. Watch
the DEBUG log for "handing off from agent to agent" lines.
"""

import logging
from strands import Agent
from strands.multiagent import Swarm
# ADDED: BedrockModel import. Without an explicit model, Agent() falls back
# to the SDK's built-in default model, which AWS has flagged "Legacy" and
# now rejects with ResourceNotFoundException. Same fix as workflow.py/graph.py.
from strands.models import BedrockModel

# Enable debug logs and print them to stderr
logging.getLogger("strands.multiagent").setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

# ADDED: explicit model pinned to a currently active Bedrock model.
# Verify active models for your account/region with:
#   aws bedrock list-inference-profiles --region us-east-1
model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-5",
    region_name="us-east-1",
)

# Create specialized agents
# ADDED: model=model on each agent (starter code had no model, which caused
# the legacy-model error).
#
# ADDED: description=... on each agent. In a Swarm, agents don't have fixed
# edges telling them who to call next - instead, Strands injects a list of
# "Other agents available for collaboration" into every agent's prompt
# before each turn, built from each agent's name + description. Without a
# description, agents only see a bare name (e.g. "Agent name: coder.") and
# have to guess what that agent does. Adding descriptions gives agents
# real information to decide who to hand off to.
#
# CHANGED FROM DOCS: the docs show these system prompts truncated with an
# ellipsis, e.g. system_prompt="You are a coding specialist...". That's the
# DOCS abbreviating for readability, not shorthand the SDK expands - copied
# literally (as this file originally did), each agent's entire instruction
# set is those five words. Written out properly below.
#
# Note the division of labor: `description` tells OTHER agents when to hand
# off to this one; `system_prompt` tells THIS agent how to do its job. Both
# matter in a swarm, and they're saying different things to different
# audiences.
researcher = Agent(
    model=model,
    name="researcher",
    description="Researches requirements, prior art, and best practices for a given task",
    system_prompt=(
        "You are a research specialist on a collaborating team. Establish "
        "what the task actually requires: constraints, prior art, and "
        "relevant best practices. Be concrete and hand off to the architect "
        "once the requirements are clear enough to design against. Do not "
        "add disclaimers about lacking live browsing access."
    ),
)
coder = Agent(
    model=model,
    name="coder",
    description="Writes implementation code based on requirements and designs",
    system_prompt=(
        "You are a coding specialist on a collaborating team. Implement the "
        "design you are given as complete, working code - not pseudocode or "
        "outlines. Include the imports and error handling a reader would "
        "need to actually run it. Hand off to the reviewer when done."
    ),
)
reviewer = Agent(
    model=model,
    name="reviewer",
    description="Reviews code for bugs, style, and best practices",
    system_prompt=(
        "You are a code review specialist on a collaborating team. Review "
        "the implementation for correctness bugs, security issues, and "
        "clarity problems. Be specific: name the line or function and say "
        "what to change. If it needs rework, hand back to the coder; if it "
        "looks solid, say so plainly and stop rather than inventing "
        "additional concerns."
    ),
)
architect = Agent(
    model=model,
    name="architect",
    description="Designs system structure and API/data models before implementation",
    system_prompt=(
        "You are a system architecture specialist on a collaborating team. "
        "Turn requirements into a concrete design: the endpoints or "
        "interfaces, the data model, and how the pieces fit together. "
        "Decide the structure so the coder does not have to guess. Hand off "
        "to the coder once the design is specific enough to implement."
    ),
)

# Create a swarm with these agents, starting with the researcher
swarm = Swarm(
    [coder, researcher, reviewer, architect],
    entry_point=researcher,  # Start with the researcher
    max_handoffs=20,
    max_iterations=20,
    execution_timeout=900.0,  # 15 minutes
    node_timeout=300.0,       # 5 minutes per agent
    repetitive_handoff_detection_window=8,  # There must be >= 3 unique agents in the last 8 handoffs
    repetitive_handoff_min_unique_agents=3
)

# ADDED: the __main__ guard. Everything below used to run at module level,
# so merely importing this file would kick off a full multi-agent Bedrock
# run. Guarding it means `import swarm` is now free, and
# `uv run python swarm.py` behaves exactly as before. Same pattern as
# every other demo in this repo.
if __name__ == "__main__":
    # Execute the swarm on a task
    result = swarm("Design and implement a simple REST API for a todo app")
    # Or use invoke_async for async execution: result = await swarm.invoke_async(...)

    # Access the final result
    print(f"\nStatus: {result.status}")
    print(f"Node history: {[node.node_id for node in result.node_history]}")

    # ADDED: print the work the swarm actually produced. The two lines
    # above only prove it RAN - they show the status enum and which agents
    # took turns, but throw away the REST API that got designed and
    # implemented, which is the whole point of the task.
    #
    # result.results is a dict keyed by node_id (same shape as graph.py).
    # node_history is ordered, so the last entry is whichever agent
    # finished last - usually the reviewer, since the swarm tends to end
    # on a review pass.
    if result.node_history:
        last_node_id = result.node_history[-1].node_id
        print("\n" + "=" * 60)
        print(f"FINAL OUTPUT (from '{last_node_id}', the agent that finished last)")
        print("=" * 60)
        print(f"\n{result.results[last_node_id]}")

        # Each agent's individual contribution is available too. Uncomment
        # to show the class the full trail - useful for pointing out that a
        # swarm accumulates work across handoffs rather than one agent
        # doing everything:
        #
        # for node_id, node_result in result.results.items():
        #     print(f"\n{'=' * 60}\n{node_id}\n{'=' * 60}\n{node_result}")