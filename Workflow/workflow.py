"""
Sequential Workflow demo.

Consolidated from the code samples on:
https://strandsagents.com/docs/user-guide/concepts/multi-agent/workflow/

RUN:
    cd Projects/Building-Advanced-Agentic-Systems-on-AWS/Workflow
    uv run python workflow.py

One process, one terminal. researcher -> analyst -> writer run in a fixed
order, each one's output feeding the next as plain text.
"""

from strands import Agent
# ADDED: BedrockModel import. The Strands docs example doesn't specify a
# model, so it relies on the SDK's built-in default model. That default
# recently got flagged "Legacy" by AWS and started throwing
# ResourceNotFoundException. Pinning an explicit, active model avoids this.
from strands.models import BedrockModel

# ADDED: explicit model pinned to a currently active Bedrock model.
# Verify active models for your account/region with:
#   aws bedrock list-inference-profiles --region us-east-1
model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-5",
    region_name="us-east-1",
)

# Create specialized agents
# ADDED: model=model on each agent (docs example omits this and falls back
# to the SDK default model, which is what caused the legacy-model error).
# CHANGED FROM DOCS: added explicit instruction not to hedge about lacking
# live/real-time access. Without this, the model tends to respond with a
# disclaimer about its knowledge cutoff instead of actually answering -
# and that disclaimer then flows downstream, causing the analyst and
# writer to produce a report ABOUT the disclaimer instead of the topic.
researcher = Agent(
    model=model,
    system_prompt=(
        "You are a research specialist. Answer using your existing "
        "knowledge. Do not comment on lacking real-time or live browsing "
        "access, and do not add disclaimers about knowledge cutoffs - "
        "just provide the most accurate, detailed information you have "
        "on the topic."
    ),
    callback_handler=None,
)
analyst = Agent(model=model, system_prompt="You analyze research data and extract insights.", callback_handler=None)
writer = Agent(model=model, system_prompt="You create polished reports based on analysis.")

# Sequential workflow processing
def process_workflow(topic):
    # Step 1: Research
    research_results = researcher(f"Research the latest developments in {topic}")

    # Step 2: Analysis
    analysis = analyst(f"Analyze these research findings: {research_results}")

    # Step 3: Report writing
    final_report = writer(f"Create a report based on this analysis: {analysis}")

    return final_report

# ADDED: everything below this line. The Strands docs snippet only defines
# process_workflow() and never calls it - it's meant as a conceptual code
# sample, not a runnable script. Without an entry point, "python workflow.py"
# just defines the function and exits, which is why nothing happened.
# The string below is the "topic" - it's passed to process_workflow(),
# which hands it to the researcher agent as its prompt. Each later agent
# only sees the previous agent's output, not this original string directly.
# Hardcoded here as a placeholder; swap it for whatever you want to demo.
if __name__ == "__main__":
    result = process_workflow("the history and evolution of AI agent frameworks leading up to modern tools like Strands")
    print(result)

    # ADDED: write the final report to a markdown file. result is an
    # AgentResult object - str(result) gives the same text print(result)
    # displays, since AgentResult defines __str__. Plain Python file I/O,
    # nothing Strands-specific here.
    output_path = "report.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(str(result))
    print(f"\nReport written to {output_path}")
# from https://strandsagents.com/docs/user-guide/concepts/multi-agent/workflow/
