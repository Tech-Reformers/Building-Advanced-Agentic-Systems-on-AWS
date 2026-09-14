# Strands Agents Tutorial

A beginner-friendly guide to building AI agents with Strands.

## What is an AI Agent?

An AI agent is an LLM (like Claude) that can:
- Understand your questions
- Decide which tools to use
- Execute those tools autonomously
- Return natural language responses

Unlike a simple chatbot, agents can take actions using the tools you give them.

## Prerequisites

- Python 3.10 or higher
- AWS account with Bedrock access
- `uv` package manager installed ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))

## Setup Instructions

### 1. Create a New Project

```bash
# Create project directory
mkdir my-agent
cd my-agent

# Initialize with uv
uv init

# Add Strands dependencies
uv add strands-agents strands-agents-tools
```

This creates:
- `main.py` - Your code goes here
- `pyproject.toml` - Project configuration
- `uv.lock` - Dependency versions (don't edit manually)
- `.venv/` - Virtual environment (auto-managed by uv)

### 2. Configure AWS Credentials

```bash
# Login to AWS (if using SSO)
aws sso login --profile your-profile-name

# Set environment variables
export AWS_PROFILE=your-profile-name
export AWS_DEFAULT_REGION=us-east-1
```

### 3. Create Your Agent

Replace the contents of `main.py` with:

```python
from strands import Agent, tool
from strands_tools import calculator, current_time

# Custom tools
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

# Create agent with both pre-built and custom tools
agent = Agent(
    tools=[
        # Pre-built tools from strands-agents-tools
        calculator,
        current_time,
        # Custom tools
        calculate_tip,
        count_characters,
        celsius_to_fahrenheit
    ],
    system_prompt="You are a helpful assistant. Answer questions directly and concisely. Only mention tools when you actually use them."
)

if __name__ == "__main__":
    print("Ask me questions (type 'quit' to exit)")
    print("I can calculate, tell time, calculate tips, count characters, and convert temperatures!")
    while True:
        question = input("\nYou: ")
        if question.lower() in ['quit', 'exit', 'q']:
            break
        agent(question)
```

### 4. Run Your Agent

```bash
uv run python main.py
```

## Understanding the Code

### Tools

Tools are Python functions decorated with `@tool`:

```python
@tool
def calculate_tip(bill_amount: float, tip_percentage: float) -> float:
    """Calculate tip amount based on bill and tip percentage."""
    return bill_amount * (tip_percentage / 100)
```

**Key parts:**
- `@tool` - Tells Strands this function is available to the agent
- Function name - The tool's name (use descriptive names!)
- Docstring (`"""..."""`) - Describes what the tool does (the LLM reads this!)
- Parameters - What inputs the tool needs
- Return value - What the tool outputs

### The Agent

```python
agent = Agent(
    tools=[calculate_tip, count_characters, celsius_to_fahrenheit],
    system_prompt="You are a helpful assistant..."
)
```

- `tools` - List of tools the agent can use
- `system_prompt` - Instructions for how the agent should behave

### Running the Agent

```python
agent("Your question here")
```

The agent:
1. Reads your question
2. Decides if it needs to use any tools
3. Calls the appropriate tools
4. Formulates a natural language response
5. Prints the response (Strands handles this automatically)

## Example Questions to Try

**Questions using pre-built tools:**
- "What time is it right now?"
- "Calculate 456 * 789"
- "What's the square root of 144?"

**Questions using custom tools:**
- "What's a 20% tip on $75?"
- "How many characters in 'Hello World'?"
- "Convert 30 Celsius to Fahrenheit"

**Questions that don't need tools:**
- "What's the capital of France?"
- "Tell me a joke"
- "Explain what an AI agent is"

**Multiple tools in one question:**
- "What time is it and what's 25 * 48?"
- "My bill is $50, I want to tip 18%. Also, what's 22 Celsius in Fahrenheit?"

## Key Concepts

### Virtual Environments (venv)

A virtual environment isolates your project's Python packages:
- Each project has its own dependencies
- No conflicts between projects
- Keeps your system Python clean

`uv` manages this automatically in the `.venv` folder.

### Why uv?

`uv` is faster and more modern than traditional `pip`:
- 10-100x faster package installation
- Better dependency resolution
- Cleaner workflow
- Becoming the Python community standard

### Agent vs Chatbot

**Chatbot:** Just answers questions
**Agent:** Can take actions using tools

The agent autonomously decides when to use tools based on your question.

## Common Issues

### "AccessDeniedException" Error

You need AWS Bedrock permissions. Make sure:
1. You're logged in: `aws sso login --profile your-profile`
2. Environment variables are set: `export AWS_PROFILE=your-profile`
3. Your AWS user has Bedrock access

### Slow Responses

This is normal! The agent:
- Sends requests to AWS Bedrock over the network
- Claude thinks and decides which tools to use
- Streams the response back

Typical response time: 3-10 seconds

### Double Output

If you see responses printed twice, remove any `print()` statements around `agent()` calls. Strands prints automatically.

## Using Pre-Built Tools

Strands provides many ready-to-use tools in the `strands-agents-tools` package:

```python
from strands import Agent
from strands_tools import calculator, current_time, shell

agent = Agent(tools=[calculator, current_time, shell])
agent("What time is it? Also calculate 25 * 48")
```

**Available pre-built tools (no API keys needed):**
- `calculator` - Perform mathematical calculations
- `current_time` - Get current date and time
- `shell` - Execute shell commands
- `python_repl` - Run Python code
- `file_read` / `file_write` - Read/write files
- And many more!

**Tools requiring API keys:**
- `tavily_search` - Web search (requires Tavily API key)
- `exa_search` - Intelligent web search (requires Exa API key)
- `bright_data` - Web scraping (requires Bright Data API key)

See the full list: [strands-agents-tools on GitHub](https://github.com/strands-agents/tools)

## Creating Your Own Tools

You can also create custom tools for your specific needs:

```python
@tool
def calculate_tip(bill_amount: float, tip_percentage: float) -> float:
    """Calculate tip amount based on bill and tip percentage."""
    return bill_amount * (tip_percentage / 100)

@tool
def word_count(text: str) -> int:
    """Count words in text."""
    return len(text.split())

@tool
def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert temperature from Fahrenheit to Celsius."""
    return (fahrenheit - 32) * 5/9
```

**Best practices:**
- Use descriptive function names
- Write clear docstrings (the LLM reads these!)
- Keep tools focused on one task
- Use type hints (`: str`, `-> int`, etc.)

**Mix pre-built and custom tools:**
```python
from strands import Agent, tool
from strands_tools import calculator, current_time

@tool
def custom_greeting(name: str) -> str:
    """Generate a personalized greeting."""
    return f"Hello {name}, great to meet you!"

agent = Agent(tools=[calculator, current_time, custom_greeting])
```

## Next Steps

- Explore the [Strands documentation](https://strandsagents.com/docs/)
- Try the `strands-agents-tools` package for pre-built tools
- Learn about multi-agent systems
- Build tools that call APIs or access databases

## Resources

- [Strands Quickstart](https://strandsagents.com/docs/user-guide/quickstart/python/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [AWS Bedrock Setup](https://docs.aws.amazon.com/bedrock/)

---

Happy agent building! 🤖
