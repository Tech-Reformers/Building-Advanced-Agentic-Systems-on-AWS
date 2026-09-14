"""
Single-agent "hello world" demo - interactive version.

Based on the quickstart on:
https://strandsagents.com/docs/user-guide/quickstart/overview/

RUN:
    cd Projects/Building-Advanced-Agentic-Systems-on-AWS
    uv run python my_agent.py

One process, one terminal. Unlike the multi-agent demos in the folders
alongside this file, this is a SINGLE agent with three custom tools - the
simplest thing in the repo, and a good first run to confirm your venv and
Bedrock credentials work before trying the bigger patterns.

It runs an interactive loop: type a question, get an answer, repeat until
you type `quit` (or `exit` / `q`). Things to try, to watch the model pick
a tool on its own:
    What's a 20% tip on $75?
    How many characters are in 'Hello World'?
    Convert 30 Celsius to Fahrenheit
    What's the capital of France?          <- needs no tool at all

RELATED FILE: my_strands_agent/my_agent.py is a similar single-agent
example, but packaged as its own standalone `uv` project (with a
pyproject.toml managing its own dependencies) and asking one hardcoded
question instead of looping. This file shares the repo-root `.venv` with
all the other demos. See my_strands_agent/README.md for that version.
"""

from strands import Agent, tool
from strands.models import BedrockModel

@tool
def calculate_tip(bill_amount: float, tip_percentage: float) -> float:
    """Calculate tip amount based on bill and tip percentage."""
    return bill_amount * (tip_percentage / 100)

@tool
def count_characters(text: str) -> int:
    """Count the number of characters in text, including spaces."""
    return len(text)

@tool
def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert temperature from Celsius to Fahrenheit."""
    return (celsius * 9/5) + 32

# Explicitly pin the model instead of relying on the SDK default,
# which can point at a model AWS has since marked legacy/inactive.
# Verify the current active model ID for your account/region with:
#   aws bedrock list-inference-profiles --region us-east-1
model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-5",
    region_name="us-east-1",
)

agent = Agent(
    model=model,
    tools=[calculate_tip, count_characters, celsius_to_fahrenheit],
    system_prompt="You are a helpful assistant. Answer questions directly and concisely. Only mention tools when you actually use them."
)

if __name__ == "__main__":
    print("Ask me questions (type 'quit' to exit)")
    while True:
        question = input("\nYou: ")
        if question.lower() in ['quit', 'exit', 'q']:
            break
        agent(question)
