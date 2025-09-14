import logging
import json
import os
from .gauntlet_master_agent import GauntletMasterAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class CrucibleMasterAgent:
    """
    Ingests and prioritizes Analysis Reports and initiates the Gauntlet Protocol for top proposals.
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.gauntlet_master = GauntletMasterAgent()

    def prioritize_reports(self, analysis_reports: list) -> list:
        # (Implementation is unchanged)
        self.logger.info(f"Prioritizing {len(analysis_reports)} reports...")
        try:
            valid_reports = [r for r in analysis_reports if "error" not in r]
            sorted_reports = sorted(
                valid_reports, key=lambda r: r.get('impact_score', 5), reverse=True
            )
            return sorted_reports
        except Exception as e:
            self.logger.error(f"Failed to sort reports: {e}"); return []

    def initiate_upgrade_gauntlet(self, top_proposal: dict):
        """
        Takes the top MIP and initiates the Gauntlet Protocol.
        """
        self.logger.info(f"--- Initiating Gauntlet Protocol for: {top_proposal.get('paper_title')} ---")
        
        # THE FIX: Extract the original paper data from the report
        original_paper = top_proposal.get("original_paper_data")
        if not original_paper:
            self.logger.error("Proposal is missing original paper data. Cannot initiate Gauntlet.")
            return

        mip_for_gauntlet = {
            "expert_agent_class": "AnalysisAgent",
            "student_agent_class": "AnalysisAgentV2",
            "curriculum": [
                { "paper": original_paper }
            ]
        }
        
        self.gauntlet_master.run_gauntlet(mip_for_gauntlet)
