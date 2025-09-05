from agents.curiosity_agent import CuriosityAgent
import os

# Ensure the temporary directory for downloads exists
if not os.path.exists("./temp_research"):
    os.makedirs("./temp_research")

def run_test():
    curiosity_agent = CuriosityAgent()
    
    proposal = curiosity_agent.run_research_cycle()

    print("\n\n========== CURIOSITY AGENT REPORT ==========")
    print(proposal)
    print("\n==========================================")

if __name__ == "__main__":
    run_test()
