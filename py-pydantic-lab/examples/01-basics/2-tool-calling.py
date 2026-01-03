from pydantic_ai import Agent, RunContext
import sys
from pathlib import Path

# Add the examples directory to sys.path to allow importing from common
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

# Import the centralized model factory.
# Rationale: Decoupling LLM selection from tool-calling logic allows us to 
# test the same tool behavior across different models easily.
from common.models import get_model

# 1. Define an agent
agent = Agent(
    get_model(),
    system_prompt="You are a helpful assistant that can check the weather and roll dice."
)

# 2. Define tools using the @agent.tool decorator
@agent.tool
def get_weather(ctx: RunContext[None], location: str) -> str:
    """Get the current weather in a given location."""
    # In a real app, this would call an API
    return f"The weather in {location} is sunny and 25°C."

@agent.tool
def roll_die(ctx: RunContext[None]) -> int:
    """Roll a 6-sided die."""
    import random
    return random.randint(1, 6)

# 3. Run the agent
def main():
    # Example 1: Weather
    prompt1 = "What is the weather like in Shanghai?"
    print(f"--- Prompt 1: {prompt1} ---")
    result1 = agent.run_sync(prompt1)
    print(f"Response: {result1.output}\n")

    # Example 2: Dice
    prompt2 = "Roll a die for me."
    print(f"--- Prompt 2: {prompt2} ---")
    result2 = agent.run_sync(prompt2)
    print(f"Response: {result2.output}")

if __name__ == '__main__':
    main()
