import json
from python_agent_runner.agents.triage_agent import TriageAgent

# Define MISO's foundational concepts as if they were research papers
miso_foundational_papers = [
    {
        "title": "ReAct: Synergizing Reasoning and Acting in Language Models",
        "summary": "Proposes a framework where Large Language Models generate both reasoning traces and task-specific actions in an interleaved manner. This allows the model to perform dynamic reasoning, tool use, and overcome limitations of simple chain-of-thought prompting by interacting with external sources."
    },
    {
        "title": "RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval",
        "summary": "Introduces a novel retrieval system that builds a tree of recursively summarized text chunks. This hierarchical structure allows for retrieval of information at different levels of abstraction, moving beyond simple document retrieval to answer complex, multi-faceted questions."
    },
    {
        "title": "Knowledge Distillation for Efficient AI Systems",
        "summary": "Presents a method for model compression where a small 'student' network is trained to mimic the outputs of a larger 'teacher' network. This transfers the knowledge to a more efficient model without significant loss of performance, which is key for creating specialized agents."
    },
    {
        "title": "Tree of Thoughts: Deliberate Problem Solving with Large Language Models",
        "summary": "An alternative to chain-of-thought prompting that allows language models to explore multiple reasoning paths at each step, creating a tree of possible thoughts. The model can self-evaluate the progress of these paths, making it more effective for complex problems where exploration is required."
    }
]

def run_retrospective():
    print("--- [MISO Retrospective Triage Test] ---")
    
    # We use a slightly lower threshold for the retrospective to see a wider range of scores
    triage_agent = TriageAgent(final_threshold=6.0)
    
    # Run the triage on our predefined list of core concepts
    triaged_results = triage_agent.run_triage(miso_foundational_papers)

    print("\n--- [RETROSPECTIVE COMPLETE] ---")
    print("The following foundational concepts were deemed relevant by the new triage protocol:")
    if triaged_results:
        print(json.dumps(triaged_results, indent=2))
    else:
        print("No concepts met the relevance threshold.")

if __name__ == "__main__":
    run_retrospective()
