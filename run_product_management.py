import os
import json
import glob
from datetime import datetime, timezone
from python_agent_runner.agents.product_manager_agent import ProductManagerAgent

def run_pm_cycle():
    """Finds the latest MIP backlog and runs the PM agent to process it."""
    print("--- [MISO Product Management Cycle Initialized] ---")
    
    output_dir = "crucible_output"
    
    # Find the most recent MIP backlog file
    backlog_files = glob.glob(os.path.join(output_dir, "mip_backlog_*.json"))
    if not backlog_files:
        print("No MIP backlog file found. Please run the Crucible Master Agent first (`run_crucible.py`).")
        return

    latest_backlog_file = max(backlog_files, key=os.path.getmtime)
    print(f"Loading backlog from: {latest_backlog_file}")

    try:
        with open(latest_backlog_file, 'r', encoding='utf-8') as f:
            mip_backlog = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading or parsing backlog file: {e}")
        return
    
    if not mip_backlog:
        print("Backlog is empty. Nothing to process.")
        return

    # Run the prioritization logic
    pm_agent = ProductManagerAgent()
    prioritized_backlog = pm_agent.process_backlog(mip_backlog)

    if prioritized_backlog:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        final_backlog_filename = os.path.join(output_dir, f"prioritized_mip_backlog_{timestamp}.json")
        
        with open(final_backlog_filename, 'w', encoding='utf-8') as f:
            json.dump(prioritized_backlog, f, indent=2)
        
        print(f"? Product Management cycle complete. Final prioritized backlog saved to: {final_backlog_filename}")
    else:
        print("?? Product Management cycle complete, but no items were prioritized.")

if __name__ == "__main__":
    run_pm_cycle()
