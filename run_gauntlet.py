import os
from python_agent_runner.agents.gauntlet_master_agent import GauntletMasterAgent

def run_gauntlet_test():
    """Defines and runs the Gauntlet competition for the AnalysisAgent."""
    print("--- [Gauntlet Protocol: AnalysisAgent Competition] ---")
    
    # The MIP to upgrade the AnalysisAgent based on the LoCoBench paper
    mip = {
        "expert_agent_class": "AnalysisAgent",
        "student_agent_class": "AnalysisAgentV2",
        "curriculum": [
            {
                "paper": {
                    "id": "http://arxiv.org/abs/2509.09614v1",
                    "title": "LoCoBench: A Benchmark for Long-Context Large Language Models",
                    "summary": "This paper introduces a benchmark and new techniques for improving performance on long-context language model tasks, suggesting alternatives to naive text chunking.",
                    "pdf_url": "http://arxiv.org/pdf/2509.09614v1"
                }
            }
        ]
    }

    master_agent = GauntletMasterAgent()
    master_agent.run_gauntlet(mip)

if __name__ == "__main__":
    run_gauntlet_test()
