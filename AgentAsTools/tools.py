"""
Agents as Tools demo.

Consolidated from the code samples on:
https://strandsagents.com/docs/user-guide/concepts/multi-agent/agents-as-tools/

RUN:
    Mac:     cd /Users/johnkrull/Projects/Building-Advanced-Agentic-Systems-on-AWS/AgentAsTools
    Windows: cd /d/Projects/Building-Advanced-Agentic-Systems-on-AWS/AgentAsTools
    uv run python tools.py

One process, one terminal. The orchestrator picks between three specialist
tools based on the query - watch the DEBUG log for which tool(s) it calls.

Pattern: a "primary" orchestrator agent doesn't do specialized work itself.
Instead, it has three specialized sub-agents wrapped as tools (research,
product recommendation, trip planning). When the orchestrator gets a user
query, the LLM decides which specialized tool(s) to call, the sub-agent runs
and returns a plain string, and the orchestrator uses that string to build
its final answer - same as it would use any other tool's return value.
"""

import logging
from strands import Agent
from strands.models import BedrockModel

# ADDED: BedrockModel import + pinned model. Without an explicit model,
# Agent() falls back to the SDK's built-in default model, which AWS has
# flagged "Legacy" and now rejects with ResourceNotFoundException. Same
# fix applied in workflow.py, graph.py, and swarm.py.
# Verify active models for your account/region with:
#   aws bedrock list-inference-profiles --region us-east-1
model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-5",
    region_name="us-east-1",
)

# Enable debug logs so students can see the orchestrator picking a tool,
# same convention used in graph.py and swarm.py.
logging.getLogger("strands").setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

RESEARCH_ASSISTANT_PROMPT = """You are a specialized research assistant. Focus only on providing
factual, well-sourced information in response to research questions.
Always cite your sources when possible."""

PRODUCT_ASSISTANT_PROMPT = """You are a specialized product recommendation assistant.
Provide personalized product suggestions based on user preferences."""

TRAVEL_ASSISTANT_PROMPT = """You are a specialized travel planning assistant.
Create detailed travel itineraries based on user preferences."""

# Create specialized agents. Each is a normal Agent, no different from any
# other agent in this project - "agents as tools" doesn't change how an
# agent is built, only how it gets used afterward.
# REMOVED: the docs example includes tools=[retrieve, http_request] on each
# specialist. Left out for this demo since retrieve needs a configured
# Bedrock Knowledge Base ID and http_request needs outbound network access -
# neither is required to demonstrate the agents-as-tools pattern itself.
# Add them back (from strands_tools) if you want these assistants to
# actually search the web or a knowledge base.
research_agent = Agent(model=model, name="research_agent", system_prompt=RESEARCH_ASSISTANT_PROMPT)
product_agent = Agent(model=model, name="product_agent", system_prompt=PRODUCT_ASSISTANT_PROMPT)
travel_agent = Agent(model=model, name="travel_agent", system_prompt=TRAVEL_ASSISTANT_PROMPT)

# .as_tool() converts an Agent into something another agent's tools=[] list
# can use. It automatically builds a tool that accepts one string input
# parameter and returns the agent's text response - equivalent to writing a
# @tool-decorated function that runs the agent and returns str(response),
# but without writing that boilerplate yourself.
#
# name= and description= are what the ORCHESTRATOR sees; they don't change
# the specialist agent at all. Write the description like a job posting -
# it's the only information the orchestrator's LLM has to decide whether
# this is the right tool for a given query.
research_tool = research_agent.as_tool(
    name="research_assistant",
    description="Process and respond to research-related queries requiring factual information.",
)
product_tool = product_agent.as_tool(
    name="product_recommendation_assistant",
    description="Provide personalized product recommendations based on user preferences.",
)
travel_tool = travel_agent.as_tool(
    name="trip_planning_assistant",
    description="Create detailed travel itineraries and provide travel advice.",
)

# NOTE ON CONTEXT: by default, .as_tool() resets the specialist's
# conversation history on every call - each invocation starts clean, with
# no memory of previous calls. Pass preserve_context=True to have the
# specialist remember prior calls within the same orchestrator session,
# e.g.: research_agent.as_tool(preserve_context=True)

# The orchestrator's system prompt is the routing logic. There's no
# if/else in Python deciding which specialist to call - the LLM reads
# these instructions and picks a tool (or several, or none) itself.
MAIN_SYSTEM_PROMPT = """You are an assistant that routes queries to specialized agents:
- For research questions and factual information -> Use the research_assistant tool
- For product recommendations and shopping advice -> Use the product_recommendation_assistant tool
- For travel planning and itineraries -> Use the trip_planning_assistant tool
- For simple questions not requiring specialized knowledge -> Answer directly
Always select the most appropriate tool based on the user's query."""

# ADDED: model=model (docs example omits it, same reason as above).
# callback_handler=None (from docs) suppresses streaming the orchestrator's
# own thinking to stdout - we print the final result ourselves below.
orchestrator = Agent(
    model=model,
    system_prompt=MAIN_SYSTEM_PROMPT,
    callback_handler=None,
    tools=[research_tool, product_tool, travel_tool],
)

# ADDED: entry point. The docs page never shows all of this assembled into
# one runnable script - it's spread across several separate snippets meant
# to be dropped into a larger project. This is the piece that makes
# "uv run python tools.py" actually do something.
if __name__ == "__main__":
    # This query intentionally spans two domains (travel + product) so
    # you can show the class the orchestrator calling multiple tools in
    # one turn and combining their answers - see the DEBUG log output for
    # each tool invocation as it happens.
    customer_query = "I'm looking for hiking boots for a trip to Patagonia next month"
    result = orchestrator(customer_query)
    print(f"\n{result}")
