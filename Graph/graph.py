"""
Graph demo.

Consolidated from the code samples on:
https://strandsagents.com/docs/user-guide/concepts/multi-agent/graph/

RUN:
    cd Projects/Building-Advanced-Agentic-Systems-on-AWS/Graph
    uv run python graph.py

One process, one terminal. research -> {analysis, fact_check} run in
parallel -> report waits for both (a join point) before running.
"""

from strands import Agent
from strands.multiagent import GraphBuilder
# ADDED: BedrockModel import. Without an explicit model, Agent() falls back
# to the SDK's built-in default model, which AWS has flagged "Legacy" and
# now rejects with ResourceNotFoundException. Same issue as workflow.py.
from strands.models import BedrockModel

# REMOVED: the DEBUG logging setup that was here. It's useful for showing
# the framework's internal node-scheduling (parallel execution, join
# points), but for a straightforward class run it buries the actual
# report output in noise. Add logging back if you want to show students
# the scheduling mechanics live.

# ADDED: explicit model pinned to a currently active Bedrock model.
# Verify active models for your account/region with:
#   aws bedrock list-inference-profiles --region us-east-1
model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-5",
    region_name="us-east-1",
)

# Create specialized agents
# ADDED: model=model on each agent (original had no model, which caused
# the legacy-model error).
#
# CHANGED FROM DOCS: the docs page shows these prompts truncated with an
# ellipsis, e.g. system_prompt="You are a research specialist...". That
# ellipsis is the DOCS abbreviating for readability - it is not shorthand
# the SDK expands. If you copy it literally (as this file originally did),
# each agent receives that seven-word string as its entire instruction set,
# and output quality suffers accordingly. Written out properly below.
#
# Same lesson as the researcher prompt in workflow.py: tell the model not
# to hedge about lacking live data, or the disclaimer flows downstream and
# later nodes end up reporting on the disclaimer instead of the topic.
researcher = Agent(
    model=model,
    name="researcher",
    system_prompt=(
        "You are a research specialist. Given a topic, lay out the key "
        "developments, players, and open questions using your existing "
        "knowledge. Be specific and concrete. Do not comment on lacking "
        "real-time or live browsing access, and do not add disclaimers "
        "about knowledge cutoffs."
    ),
)
analyst = Agent(
    model=model,
    name="analyst",
    system_prompt=(
        "You are a data analysis specialist. Take the research you are "
        "given and extract the significant patterns, tradeoffs, and "
        "implications. Prioritize insight over summary - say what the "
        "findings MEAN, not just what they say."
    ),
)
fact_checker = Agent(
    model=model,
    name="fact_checker",
    system_prompt=(
        "You are a fact checking specialist. Review the research you are "
        "given and flag any claim that is inaccurate, overstated, missing "
        "important context, or presented with more confidence than the "
        "evidence supports. State clearly which claims you could not "
        "verify. If a claim checks out, say so briefly and move on."
    ),
)
report_writer = Agent(
    model=model,
    name="report_writer",
    system_prompt=(
        "You are a report writing specialist. You receive an analysis and "
        "a fact check of the same research. Produce a clear, well-organized "
        "report in markdown that incorporates the analyst's insights and "
        "respects the fact checker's corrections - if the two disagree, "
        "defer to the fact checker and note the uncertainty."
    ),
)

# Build the graph
builder = GraphBuilder()

# Add nodes
builder.add_node(researcher, "research")
builder.add_node(analyst, "analysis")
builder.add_node(fact_checker, "fact_check")
builder.add_node(report_writer, "report")

# Add edges (dependencies)
builder.add_edge("research", "analysis")
builder.add_edge("research", "fact_check")
builder.add_edge("analysis", "report")
builder.add_edge("fact_check", "report")

# Set entry points (optional - will be auto-detected if not specified)
builder.set_entry_point("research")

# Optional: Configure execution limits for safety
builder.set_execution_timeout(600)   # 10 minute timeout

# Build the graph
graph = builder.build()

# ADDED: the __main__ guard. Everything below used to run at module level,
# which meant merely importing this file (e.g. to inspect the graph object
# in a REPL) would kick off a full four-agent Bedrock run. Guarding it
# means `import graph` is now free, and `uv run python graph.py` behaves
# exactly as before. Every other demo in this repo uses this same pattern.
if __name__ == "__main__":
    # Execute the graph on a task
    result = graph("Research the impact of AI on ophthalmology and create a comprehensive report")
    # Or use invoke_async for async execution: result = await graph.invoke_async(...)

    # Access the results
    print(f"\nStatus: {result.status}")
    print(f"Execution order: {[node.node_id for node in result.execution_order]}")

    # ADDED: print the report itself, not just the metadata above. Status
    # and execution order tell you the graph RAN; they don't show what it
    # produced. The report node's text is the actual deliverable.
    print("\n" + "=" * 60)
    print("FINAL REPORT (from the 'report' node)")
    print("=" * 60)
    print(f"\n{result.results['report']}")

    # ADDED: write the final report node's output to a markdown file, same
    # pattern as workflow.py. result.results is a dict keyed by node_id
    # ("research", "analysis", "fact_check", "report") - we want just the
    # "report" node's text, not all four nodes concatenated, since that's
    # what a user would expect "the report" to mean. str(node_result) gives
    # the same text you'd see printed for that node.
    #
    # NOTE: workflow.py writes a report.md too. Both write to the current
    # working directory, so running them from the same folder overwrites -
    # run each from its own folder (as the RUN block says) to keep both.
    output_path = "report.md"
    report_text = str(result.results["report"])
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"\nReport written to {output_path}")