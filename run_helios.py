import os
import json
from datetime import datetime, timezone
from python_agent_runner.agents.horizon_scanning_agent import HorizonScanningAgent
from python_agent_runner.agents.triage_agent import TriageAgent
from python_agent_runner.agents.analysis_agent import AnalysisAgent

def run_pipeline():
    """Runs the full Scan -> Triage -> Analyze pipeline."""
    print("--- [Helios Protocol: Phase 1 - Horizon Scan] ---")
    
    scan_agent = HorizonScanningAgent()
    papers = scan_agent.scan_for_research()

    if not papers:
        print("?? Scan complete. No new papers were found, or an error occurred.")
        return

    output_dir = "crucible_output"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    
    scan_filename = os.path.join(output_dir, f"scan_results_{timestamp}.json")
    with open(scan_filename, 'w', encoding='utf-8') as f: json.dump(papers, f, indent=2)
    print(f"? Scan complete. Full results saved to: {scan_filename}")

    # Phase 2: Triage
    print("\n--- [Helios Protocol: Phase 2 - Triage] ---")
    triage_agent = TriageAgent()
    triaged_papers = triage_agent.run_triage(papers)

    if not triaged_papers:
        print("?? Triage complete. No papers met the relevance threshold.")
        return

    triage_filename = os.path.join(output_dir, f"triage_results_{timestamp}.json")
    with open(triage_filename, 'w', encoding='utf-8') as f: json.dump(triaged_papers, f, indent=2)
    print(f"? Triage complete. High-relevance papers saved to: {triage_filename}")

    # Phase 3: Analysis
    print("\n--- [Helios Protocol: Phase 3 - Deep Analysis] ---")
    analysis_agent = AnalysisAgent()
    analysis_dir = os.path.join(output_dir, f"analysis_reports_{timestamp}")
    os.makedirs(analysis_dir, exist_ok=True)
    print(f"Saving detailed analysis reports to: {analysis_dir}")

    for i, paper in enumerate(triaged_papers):
        print(f"\nAnalyzing paper {i + 1}/{len(triaged_papers)}: '{paper.get('title')[:60]}...'")
        report = analysis_agent.analyze_paper(paper)
        
        report_filename = os.path.join(analysis_dir, f"{paper.get('id').split('/')[-1].replace('.', '_')}.json")
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print(f"? Analysis complete. Report saved to: {report_filename}")

if __name__ == "__main__":
    run_pipeline()
