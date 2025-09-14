import json
from python_agent_runner.agents.genesis_agent import GenesisAgent

print("--- [MISO Full Pipeline Validation Test] ---")

# A proposal designed to test the full Plan -> Simulate -> Generate -> Debug -> Secure pipeline.
test_proposal = {
    "project_name": "Simple Python Calculator",
    "objective": "Create a single Python script named calculator.py. The script should define a function add(a, b) that returns the sum of two numbers. It should also include a main execution block that calls this function with two numbers (e.g., 5 and 7) and prints the result to the console."
}
print(f"Submitting proposal: {test_proposal['project_name']}")

# Instantiate and invoke the GenesisAgent
genesis_agent = GenesisAgent()
print("Invoking the GenesisAgent pipeline...")
result = genesis_agent.create_codebase(test_proposal)

# Print the final result
print("\n--- [PIPELINE COMPLETE] ---")
print(json.dumps(result, indent=2))
