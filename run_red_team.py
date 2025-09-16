import os
import json
from python_agent_runner.agents.security_agent import SecurityAgent

def run_test():
    """Initializes and runs a Red Team test on the latest generated project."""
    print("--- [MISO Red Team Test Initialized] ---")
    
    # For this test, we'll target the last project we created
    project_path = "generated_projects/create_a_simple_web-based"
    
    if not os.path.exists(project_path):
        print(f"Error: Project path not found at '{project_path}'. Please generate a project first.")
        return

    print(f"Targeting project: {project_path}")
    
    agent = SecurityAgent()
    report = agent.run_red_team_test(project_path)

    print("\n--- [RED TEAM TEST COMPLETE] ---")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run_test()
