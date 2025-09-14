import os
import json
import glob
from datetime import datetime, timezone
from python_agent_runner.agents.crucible_master_agent import CrucibleMasterAgent

def run_master_agent():
    """Finds the latest analysis reports and runs the master agent to prioritize them."""
    print("--- [Crucible Master Agent Initialized] ---")
    
    output_dir = "crucible_output"
    
    # Find the most recent directory of analysis reports
    analysis_dirs = glob.glob(os.path.join(output_dir, "analysis_reports_*"))
    if not analysis_dirs:
        print("No analysis report directories found. Please run the Helios protocol first (`run_helios.py`).")
        return

    latest_analysis_dir = max(analysis_dirs, key=os.path.getmtime)
    print(f"Loading reports from: {latest_analysis_dir}")

    # Load all individual JSON reports from that directory
    analysis_reports = []
    report_files = glob.glob(os.path.join(latest_analysis_dir, "*.json"))
    for report_file in report_files:
        with open(report_file, 'r', encoding='utf-8') as f:
            try:
                analysis_reports.append(json.load(f))
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON from {report_file}. Skipping.")
    
    if not analysis_reports:
        print("No valid analysis reports found in the latest directory.")
        return

    # Run the prioritization logic
    master_agent = CrucibleMasterAgent()
    mip_backlog = master_agent.prioritize_reports(analysis_reports)

    if mip_backlog:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        backlog_filename = os.path.join(output_dir, f"mip_backlog_{timestamp}.json")
        
        with open(backlog_filename, 'w', encoding='utf-8') as f:
            json.dump(mip_backlog, f, indent=2)
        
        print(f"? Prioritization complete. MISO Improvement Proposal backlog saved to: {backlog_filename}")
    else:
        print("?? Prioritization complete, but no valid proposals were generated.")

if __name__ == "__main__":
    run_master_agent()
