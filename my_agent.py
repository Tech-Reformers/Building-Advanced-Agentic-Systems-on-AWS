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
