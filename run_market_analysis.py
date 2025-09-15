import os
import json
from datetime import datetime, timezone
from python_agent_runner.agents.market_agent import MarketAgent

def run_analysis():
    """Initializes and runs the MarketAgent, saving the results."""
    print("--- [MISO Market Analysis Initialized] ---")
    
    agent = MarketAgent()
    report = agent.analyze_market_trends()

    if "error" not in report:
        output_dir = "crucible_output"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        filename = os.path.join(output_dir, f"market_analysis_report_{timestamp}.json")

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"? Market analysis complete. Report saved to: {filename}")
        print("\n--- Top Trends ---")
        for trend in report.get("trends", []):
            print(f"{trend.get('rank')}. {trend.get('project_category')}: {trend.get('opportunity_analysis')}")

    else:
        print(f"?? Market analysis failed: {report.get('error')}")

if __name__ == "__main__":
    run_analysis()
