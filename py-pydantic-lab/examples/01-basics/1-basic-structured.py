from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from dotenv import load_dotenv
import os

import sys
from pathlib import Path

# Add the examples directory to sys.path to allow importing from common
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

# Import the centralized model factory.
# Architectural Note: This follows the Dependency Inversion Principle, where
# our Agent logic depends on an abstraction (get_model) rather than a concrete
# provider implementation.
from common.models import get_model

# 1. Define the structure of the output you want
class UserProfile(BaseModel) :
    name: str
    age: int
    interests: list[str]
    summary: str

# 2. Initialize the Agent with output_type (v1.x pattern)
agent = Agent(
    get_model(),
    output_type=UserProfile,
    system_prompt='Extract user information from the provided text.'
)

# 3. Run the agent
def main():
    user_input = "Hi, I'm Gavin. I'm 25 years old and I love coding in Node.js, exploring AI agents, and playing basketball."
    
    print(f"--- Input ---\n{user_input}\n")
    
    # Run synchronously
    result = agent.run_sync(user_input)
    
    print("--- Structured Output ---")
    # In v1.x, we use result.output to access the structured data
    print(f"Name: {result.output.name}")
    print(f"Age: {result.output.age}")
    print(f"Interests: {', '.join(result.output.interests)}")
    print(f"Summary: {result.output.summary}")
    
    # Usage information
    print(f"\n--- Usage ---")
    print(result.usage())

if __name__ == '__main__':
    main()
