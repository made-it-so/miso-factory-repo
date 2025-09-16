import os
import json
import glob
from datetime import datetime, timezone
from python_agent_runner.agents.codex_indexer_agent import CodexIndexerAgent

def run_indexer():
    """Finds the latest generated project and runs the Codex Indexer agent on it."""
    print("--- [MISO Codex Indexing Initialized] ---")
    
    project_base_dir = "generated_projects"
    
    # Find all subdirectories in the base directory
    try:
        project_dirs = [os.path.join(project_base_dir, d) for d in os.listdir(project_base_dir) if os.path.isdir(os.path.join(project_base_dir, d))]
        if not project_dirs:
            print(f"No generated project directories found in '{project_base_dir}'. Please run the Genesis pipeline first.")
            return
    except FileNotFoundError:
        print(f"Directory '{project_base_dir}' not found. Please run the Genesis pipeline first.")
        return

    latest_project_dir = max(project_dirs, key=os.path.getmtime)
    print(f"Found latest project to index: {latest_project_dir}")

    # Run the indexing process
    indexer_agent = CodexIndexerAgent()
    knowledge_tree = indexer_agent.index_project(latest_project_dir)

    if knowledge_tree and "error" not in knowledge_tree:
        output_dir = "crucible_output"
        os.makedirs(output_dir, exist_ok=True)
        
        project_name = os.path.basename(latest_project_dir)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        codex_filename = os.path.join(output_dir, f"codex_tree_{project_name}_{timestamp}.json")
        
        with open(codex_filename, 'w', encoding='utf-8') as f:
            json.dump(knowledge_tree, f, indent=2)
        
        print(f"? Codex indexing complete. Knowledge tree saved to: {codex_filename}")
    else:
        print(f"?? Codex indexing failed: {knowledge_tree.get('error', 'Unknown error')}")

if __name__ == "__main__":
    run_indexer()
