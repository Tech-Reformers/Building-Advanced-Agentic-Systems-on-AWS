from strands import Agent, tool
from strands.models import BedrockModel

@tool
def word_count(text: str) -> int:
    """Count words in text."""
    return len(text.split())

@tool
def reverse_text(text: str) -> str:
    """Reverse the given text."""
    return text[::-1]

# Explicitly pin the model instead of relying on the SDK default,
# which can point at a model AWS has since marked legacy/inactive.
# Verify the current active model ID for your account/region with:
#   aws bedrock list-inference-profiles --region us-east-1
model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-5",
    region_name="us-east-1",
)

# Create agent with tools
agent = Agent(model=model, tools=[word_count, reverse_text])

# Run the agent
if __name__ == "__main__":
    response = agent("How many words are in 'Hello world from Strands'?")
    print(response)
