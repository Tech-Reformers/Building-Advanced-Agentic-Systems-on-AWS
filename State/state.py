"""
State Management demo.

Consolidated from the code samples on:
https://strandsagents.com/docs/user-guide/concepts/agents/state/

RUN:
    Mac:     cd /Users/johnkrull/Projects/Building-Advanced-Agentic-Systems-on-AWS/State
    Windows: cd /d/Projects/Building-Advanced-Agentic-Systems-on-AWS/State
    uv run python state.py

One process, one terminal. Prints each of the three state types as it
goes, so you can point at the output and the matching section in the
docs at the same time.

Strands agents maintain state in THREE distinct forms - this demo covers
all three, one after another:

  1. Conversation History (agent.messages)
     The back-and-forth of user/assistant messages. IS sent to the model
     on every call. This is what the model actually "sees."

  2. Agent State (agent.state)
     Key-value storage that lives OUTSIDE the conversation. NOT sent to
     the model. Survives across multiple agent() calls. Good for things
     like counters, user preferences, session flags - data your tools
     and app code need, but that the model doesn't need to read directly.

  3. Invocation State (result.state)
     A dict that exists only for the duration of ONE agent() call. Shared
     by reference across hooks/tools during that call, then gone. Also
     NOT sent to the model.

Quick way to tell them apart: conversation history is what the MODEL
remembers. Agent state is what your CODE remembers across calls.
Invocation state is scratch space for ONE call and then it's gone.
"""

import logging
from strands import Agent, tool, ToolContext
from strands.models import BedrockModel

# ADDED: BedrockModel import + pinned model. Without an explicit model,
# Agent() falls back to the SDK's built-in default model, which AWS has
# flagged "Legacy" and now rejects with ResourceNotFoundException. Same
# fix applied in every other demo file in this project.
# Verify active models for your account/region with:
#   aws bedrock list-inference-profiles --region us-east-1
model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-5",
    region_name="us-east-1",
)

# CHANGED FROM OTHER DEMOS: WARNING instead of DEBUG. The other demo
# files use DEBUG because watching the framework's internal log lines IS
# part of the point (e.g. seeing Swarm handoffs, Graph node execution
# order). This demo's point is the print() output below - four state
# types, back to back. DEBUG logging buries that in tool-registry noise
# between every print(), which is what made this file hard to follow
# live. Bump back to DEBUG yourself if you want to show the plumbing.
logging.getLogger("strands").setLevel(logging.WARNING)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)


def pause_for_class() -> None:
    """ADDED: a manual checkpoint between parts.

    All 4 parts used to fire back-to-back the moment you ran the script -
    for a live audience, that's a lot of output to read while also
    fielding questions. input() blocks until you press Enter, so you
    control the pace: talk through the part that just printed, then hit
    Enter when you're ready for the next one.
    """
    input("\n>>> Press Enter to continue to the next part...\n")


# ---------------------------------------------------------------------------
# Part 3 setup: tools that read/write AGENT STATE (not model context).
# These have to be defined before the Agent is created, since they're
# passed into Agent(tools=[...]) below.
# ---------------------------------------------------------------------------

# @tool(context=True) + a tool_context: ToolContext parameter is how a
# tool gets access to the agent it's attached to - specifically
# tool_context.agent.state here. Without context=True, a tool has no way
# to reach the agent's state store at all.
@tool(context=True)
def track_user_action(action: str, tool_context: ToolContext) -> str:
    """Track user actions in agent state.

    Args:
        action: The action to track
    """
    # Get current action count. agent.state.get(key) returns None if the
    # key was never set - "or 0" gives us a starting value.
    action_count = tool_context.agent.state.get("action_count") or 0
    # Update state. This write is NOT part of the conversation the model
    # sees - it's separate key-value storage the model has no visibility
    # into unless a tool explicitly reports it back (which we do below).
    tool_context.agent.state.set("action_count", action_count + 1)
    tool_context.agent.state.set("last_action", action)
    return f"Action '{action}' recorded. Total actions: {action_count + 1}"


@tool(context=True)
def get_user_stats(tool_context: ToolContext) -> str:
    """Get user statistics from agent state."""
    action_count = tool_context.agent.state.get("action_count") or 0
    last_action = tool_context.agent.state.get("last_action") or "none"
    return f"Actions performed: {action_count}, Last action: {last_action}"


# ADDED: model=model + callback_handler=None (docs example omits both;
# model for the legacy-model fix, callback_handler=None so our own
# print() calls are the only thing writing to stdout - same convention
# as workflow.py/tools.py/memory.py).
#
# ADDED: state={...} initial value. The docs show this as a SEPARATE
# example further down the page (a plain Agent() with no tools). We
# start non-zero here (session_count already at 3) so the "state existed
# before this conversation started" point is visible without having to
# run the script multiple times.
agent = Agent(
    model=model,
    tools=[track_user_action, get_user_stats],
    state={"user_preferences": {"theme": "dark"}, "session_count": 3},
    callback_handler=None,
)


if __name__ == "__main__":
    # -----------------------------------------------------------------
    # Part 1: Conversation History
    # -----------------------------------------------------------------
    print("=" * 60)
    print("PART 1: Conversation History (agent.messages)")
    print("=" * 60)

    result = agent("Hi, my name is Strands!")
    print(f"\n{result}")

    result = agent("What's my name?")
    print(f"\n{result}")

    # agent.messages is the literal list sent to the model on every call -
    # every user turn, every assistant reply, every tool call/result.
    print(f"\nConversation history has {len(agent.messages)} messages:")
    for i, msg in enumerate(agent.messages):
        role = msg["role"]
        # Message content is a list of blocks (text, toolUse, toolResult).
        # Grab just the text for a compact printout.
        text_parts = [b.get("text", f"<{list(b.keys())[0]}>") for b in msg["content"]]
        print(f"  [{i}] {role}: {' '.join(text_parts)[:80]}")

    pause_for_class()

    # -----------------------------------------------------------------
    # Part 2: Agent State - direct get/set/delete, no tools involved
    # -----------------------------------------------------------------
    print("\n" + "=" * 60)
    print("PART 2: Agent State (agent.state) - direct access")
    print("=" * 60)

    # Values already set at construction time (state={...} above).
    print(f"\nuser_preferences: {agent.state.get('user_preferences')}")
    print(f"session_count (initial): {agent.state.get('session_count')}")

    # Agent state enforces JSON-serializable values only - this is what
    # lets it be persisted/restored later (e.g. via Session Management).
    agent.state.set("last_action", "login")
    agent.state.set("session_count", 4)
    print(f"session_count (after set): {agent.state.get('session_count')}")

    # agent.state.get() with no key returns the WHOLE state dict.
    print(f"Entire state dict: {agent.state.get()}")

    agent.state.delete("last_action")
    print(f"After delete, last_action: {agent.state.get('last_action')}")

    # Non-JSON-serializable values raise ValueError - this is what the
    # docs mean by "state validation and safety."
    try:
        agent.state.set("bad_value", lambda x: x)
    except ValueError as e:
        print(f"\nExpected error setting a non-serializable value: {e}")

    pause_for_class()

    # -----------------------------------------------------------------
    # Part 3: Agent State via TOOLS - the same state store, but read and
    # written by the model calling tools instead of our own code calling
    # agent.state directly. This is the "Using State in Tools" section.
    # -----------------------------------------------------------------
    print("\n" + "=" * 60)
    print("PART 3: Agent State via Tools (the model drives this)")
    print("=" * 60)

    # The model decides to call track_user_action based on the prompt -
    # we never call the tool directly. Each call mutates agent.state
    # under the hood via tool_context.agent.state.set(...).
    result = agent("Track that I logged in")
    print(f"\n{result}")

    result = agent("Track that I viewed my profile")
    print(f"\n{result}")

    # Read the SAME state values back directly, without going through a
    # tool - proving it's one shared store regardless of how it's touched.
    print(f"\nDirect read - action_count: {agent.state.get('action_count')}")
    print(f"Direct read - last_action: {agent.state.get('last_action')}")

    # Ask the model to read it back too, via the get_user_stats tool.
    result = agent("What are my user stats?")
    print(f"\n{result}")

    pause_for_class()

    # -----------------------------------------------------------------
    # Part 4: Invocation State - scratch space for a SINGLE agent() call
    # -----------------------------------------------------------------
    print("\n" + "=" * 60)
    print("PART 4: Invocation State (result.state) - one call, then gone")
    print("=" * 60)

    # ADDED: this whole section. The docs show invocation_state via a
    # custom callback_handler counting events - but our agent above has
    # callback_handler=None (so nothing double-prints, see PART 1-3).
    # Instead we build a SEPARATE agent just for this part, with its own
    # callback handler, to keep the demos from interfering with each other.
    def custom_callback_handler(**kwargs):
        if "request_state" in kwargs:
            state = kwargs["request_state"]
            if "counter" not in state:
                state["counter"] = 0
            state["counter"] += 1
            print(f"  (callback fired - event count so far: {state['counter']})")

    invocation_demo_agent = Agent(model=model, callback_handler=custom_callback_handler)
    result = invocation_demo_agent("Hi there!")
    print(f"\nFinal invocation state for this one call: {result.state}")
    print(
        "Note: this dict is fresh and empty on the NEXT call - it does not "
        "persist like agent.state does. Run this script again and "
        "session_count/action_count pick up nowhere (they reset, since "
        "this demo never saves agent.state to disk) - but within a single "
        "invocation, request_state is shared across every hook/tool call."
    )
