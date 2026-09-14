"""
Prompt Caching demo.

Consolidated from the code samples on:
https://strandsagents.com/docs/user-guide/concepts/model-providers/amazon-bedrock/
(the "Prompt Caching" section of the Bedrock model provider page)

RUN:
    Mac:     cd /Users/johnkrull/Projects/Building-Advanced-Agentic-Systems-on-AWS/Cache
    Windows: cd /d/Projects/Building-Advanced-Agentic-Systems-on-AWS/Cache
    uv run python cache.py

One process, one terminal. Makes several calls back to back and prints
cache write/read token counts after each one, so you can watch a cache
get written on the first call and read on later calls.

Pattern: Bedrock can cache parts of a prompt (system prompt, tools,
messages) so repeated requests that share that content don't have to pay
full price or full latency for it every time. A "cache write" happens the
first time Bedrock sees a given block of content; a "cache read" happens
on a later request that reuses the exact same content.

Three ways to use it, all shown below:
  Part 1: System Prompt Caching  - cache a big, unchanging system prompt
  Part 2: Tool Caching           - cache the tool definitions
  Part 3: CacheConfig(strategy="auto") - the SDK manages cache points for
          you across a multi-turn conversation, instead of placing them
          by hand.

Cache reads are billed at a lower rate than normal input tokens - that's
the cost benefit. The latency benefit is real too, but token counts are
what's easy to show live.
"""

import logging
from strands import Agent, tool
from strands.models import BedrockModel, CacheConfig
from strands.types.content import SystemContentBlock
from strands_tools import calculator, current_time

# Keep logging quiet - the point of this demo is the printed cache
# metrics, not framework internals. Same choice made in state.py.
logging.getLogger("strands").setLevel(logging.WARNING)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)


def print_cache_metrics(label: str, response) -> None:
    """ADDED: shared helper so every part below prints metrics the same
    way. response.metrics.accumulated_usage is a dict-like object -
    .get(..., 0) is used because a key is absent entirely when no cache
    activity happened, not just zero.
    """
    usage = response.metrics.accumulated_usage
    cache_write = usage.get("cacheWriteInputTokens", 0)
    cache_read = usage.get("cacheReadInputTokens", 0)
    print(f"{label} -> cache write: {cache_write}, cache read: {cache_read}")


# ---------------------------------------------------------------------------
# Part 1: System Prompt Caching (manual cache point)
# ---------------------------------------------------------------------------
# ADDED: wrapped in a function so Part 1/2/3 don't share module-level
# agents by accident - each part builds and uses its own agent.
def part1_system_prompt_caching() -> None:
    print("=" * 60)
    print("PART 1: System Prompt Caching")
    print("=" * 60)

    # Prompt caching has a MINIMUM TOKEN requirement per model (e.g.
    # 1,024 tokens for Claude Sonnet) - content below that threshold
    # never gets cached at all. The "* 1600" repetition here is what
    # pushes this short sentence over that minimum so caching actually
    # kicks in - this is purely to make the demo trigger caching, real
    # system prompts are usually already long enough on their own
    # (detailed instructions, examples, reference docs, etc.).
    system_content = [
        SystemContentBlock(
            text="You are a helpful assistant..." * 1600
        ),
        # cachePoint marks "everything before this point is cacheable."
        # Content must be BYTE-FOR-BYTE identical on the next request to
        # produce a cache read - any edit invalidates it.
        SystemContentBlock(cachePoint={"type": "default"}),
    ]

    # ADDED: model_id pinned explicitly. Agent(system_prompt=...) below
    # uses the SDK's default model unless we build a BedrockModel first -
    # same legacy-model fix as every other demo file in this project.
    # Verify active models for your account/region with:
    #   aws bedrock list-inference-profiles --region us-east-1
    model = BedrockModel(
        model_id="us.anthropic.claude-sonnet-5",
        region_name="us-east-1",
    )
    agent = Agent(model=model, system_prompt=system_content, callback_handler=None)

    # First request WRITES the system prompt to cache (cache write > 0).
    response1 = agent("Tell me about Python")
    print(f"\n{response1}")
    print_cache_metrics("Call 1 (Python)", response1)

    # Second request reuses the identical cached system prompt content,
    # so it READS from cache instead of paying full price again
    # (cache read > 0, cache write should now be 0 or near 0).
    response2 = agent("Tell me about JavaScript")
    print(f"\n{response2}")
    print_cache_metrics("Call 2 (JavaScript)", response2)


# ---------------------------------------------------------------------------
# Part 2: Tool Caching
# ---------------------------------------------------------------------------
def part2_tool_caching() -> None:
    print("\n" + "=" * 60)
    print("PART 2: Tool Caching")
    print("=" * 60)

    # cache_tools="default" caches the TOOL DEFINITIONS (names,
    # descriptions, input schemas) that get sent to the model on every
    # call - separate from caching the system prompt or messages.
    model = BedrockModel(
        model_id="us.anthropic.claude-sonnet-5",
        region_name="us-east-1",
        cache_tools="default",
    )
    agent = Agent(model=model, tools=[calculator, current_time], callback_handler=None)

    # First call writes the tool definitions to cache.
    response1 = agent("What time is it?")
    print(f"\n{response1}")
    print_cache_metrics("Call 1 (time)", response1)

    # Second call reuses the cached tool definitions - same tools,
    # different question, so the tool schemas are unchanged.
    response2 = agent("What is the square root of 1764?")
    print(f"\n{response2}")
    print_cache_metrics("Call 2 (square root)", response2)


# ---------------------------------------------------------------------------
# Part 3: CacheConfig(strategy="auto") - hands-off cache management
# ---------------------------------------------------------------------------
def part3_auto_cache_strategy() -> None:
    print("\n" + "=" * 60)
    print('PART 3: CacheConfig(strategy="auto")')
    print("=" * 60)

    # This is a plain function tool (not Bedrock-hosted) that returns
    # a long-ish canned string, just so there's real message content
    # for the conversation cache to build up across turns.
    @tool
    def web_search(query: str) -> str:
        """Search the web for information."""
        return f"""
        Search results for '{query}':
        1. Comprehensive Guide - [Long article with detailed explanations
           of async patterns, error handling, and best practices...]
        2. Research Paper - [Detailed findings and methodology covering
           performance benchmarks across multiple runtimes...]
        3. Stack Overflow - [Multiple answers and code snippets discussing
           tradeoffs between approaches...]
        """

    # strategy="auto" (Claude models only) does TWO things automatically,
    # both described on the docs page:
    #   1. Caches the system prompt by default (like Part 1, but without
    #      you placing a SystemContentBlock cachePoint by hand).
    #   2. Places a cache point at the end of the last user message on
    #      every call, so a multi-turn conversation's accumulated
    #      history gets cached too - not just the system prompt.
    model = BedrockModel(
        model_id="us.anthropic.claude-sonnet-5",
        region_name="us-east-1",
        cache_config=CacheConfig(strategy="auto"),
    )
    agent = Agent(model=model, tools=[web_search], callback_handler=None)

    # First call: cache write as the system prompt + this turn's content
    # get cached for the first time.
    response1 = agent("Search for Python async patterns, then compare with error handling")
    print(f"\n{response1}")
    print_cache_metrics("Call 1 (search + compare)", response1)

    # Follow-up: reuses the cached system prompt AND the cached
    # conversation history from call 1 - this is the "accumulated
    # context" benefit strategy="auto" is built for.
    response2 = agent("Summarize the key differences")
    print(f"\n{response2}")
    print_cache_metrics("Call 2 (follow-up)", response2)


# ADDED: entry point + the pause between parts. The docs page shows each
# part as an isolated snippet - this assembles all three into one
# runnable script, and pauses between them so you can talk through one
# part's cache metrics before moving to the next during class.
if __name__ == "__main__":
    part1_system_prompt_caching()
    input("\n>>> Press Enter to continue to Part 2 (Tool Caching)...\n")

    part2_tool_caching()
    input('\n>>> Press Enter to continue to Part 3 (CacheConfig auto)...\n')

    part3_auto_cache_strategy()

    print("\n" + "=" * 60)
    print("Done. Note: caches expire after 5 minutes of inactivity, and")
    print("ANY change to cached content (even one character) invalidates")
    print("it on the next request - that's why write/read numbers can")
    print("look different than expected if you re-run parts individually.")
    print("=" * 60)
