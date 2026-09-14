"""
Swarm demo.

Consolidated from the code samples on:
https://strandsagents.com/docs/user-guide/concepts/multi-agent/swarm/

RUN:
    Mac:     cd /Users/johnkrull/Projects/Building-Advanced-Agentic-Systems-on-AWS/Swarm
    Windows: cd /d/Projects/Building-Advanced-Agentic-Systems-on-AWS/Swarm
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
# ADDED: description=... on each agent. In a Swarm, agents don't have fixed
# edges telling them who to call next - instead, Strands injects a list of
# "Other agents available for collaboration" into every agent's prompt
# before each turn, built from each agent's name + description. Without a
# description, agents only see a bare name (e.g. "Agent name: coder.") and
# have to guess what that agent does. Adding descriptions gives agents
# real information to decide who to hand off to.
researcher = Agent(model=model, name="researcher", description="Researches requirements, prior art, and best practices for a given task", system_prompt="You are a research specialist...")
coder = Agent(model=model, name="coder", description="Writes implementation code based on requirements and designs", system_prompt="You are a coding specialist...")
reviewer = Agent(model=model, name="reviewer", description="Reviews code for bugs, style, and best practices", system_prompt="You are a code review specialist...")
architect = Agent(model=model, name="architect", description="Designs system structure and API/data models before implementation", system_prompt="You are a system architecture specialist...")

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

# Execute the swarm on a task
result = swarm("Design and implement a simple REST API for a todo app")
# Or use invoke_async for async execution: result = await swarm.invoke_async(...)

# Access the final result
print(f"Status: {result.status}")
print(f"Node history: {[node.node_id for node in result.node_history]}")