"""
Graph demo.

Consolidated from the code samples on:
https://strandsagents.com/docs/user-guide/concepts/multi-agent/graph/

RUN:
    Mac:     cd /Users/johnkrull/Projects/Building-Advanced-Agentic-Systems-on-AWS/Graph
    Windows: cd /d/Projects/Building-Advanced-Agentic-Systems-on-AWS/Graph
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
researcher = Agent(model=model, name="researcher", system_prompt="You are a research specialist...")
analyst = Agent(model=model, name="analyst", system_prompt="You are a data analysis specialist...")
fact_checker = Agent(model=model, name="fact_checker", system_prompt="You are a fact checking specialist...")
report_writer = Agent(model=model, name="report_writer", system_prompt="You are a report writing specialist...")

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

# Execute the graph on a task
result = graph("Research the impact of AI on Opthalmology and create a comprehensive report")
# Or use invoke_async for async execution: result = await graph.invoke_async(...)

# Access the results
print(f"\nStatus: {result.status}")
print(f"Execution order: {[node.node_id for node in result.execution_order]}")

# ADDED: write the final report node's output to a markdown file, same
# pattern as workflow.py. result.results is a dict keyed by node_id
# ("research", "analysis", "fact_check", "report") - we want just the
# "report" node's text, not all four nodes concatenated, since that's
# what a user would expect "the report" to mean. str(node_result) gives
# the same text you'd see printed for that node.
output_path = "report.md"
report_text = str(result.results["report"])
with open(output_path, "w", encoding="utf-8") as f:
    f.write(report_text)
print(f"\nReport written to {output_path}")