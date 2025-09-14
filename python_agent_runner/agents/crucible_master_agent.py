import logging
import json
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class CrucibleMasterAgent:
    """
    Ingests and prioritizes Analysis Reports to create a backlog of MISO Improvement Proposals (MIPs).
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("CrucibleMasterAgent initialized.")

    def prioritize_reports(self, analysis_reports: list) -> list:
        """
        Prioritizes a list of analysis reports.
        For V1, this uses a simple sort by the 'impact_score'.
        """
        self.logger.info(f"Prioritizing {len(analysis_reports)} analysis reports...")
        try:
            # Filter out any reports that have errors or are missing an impact score
            valid_reports = [r for r in analysis_reports if "error" not in r and r.get("impact_score") is not None]
            
            sorted_reports = sorted(
                valid_reports,
                key=lambda r: r.get('impact_score', 0),
                reverse=True
            )
            self.logger.info(f"Successfully prioritized {len(sorted_reports)} valid reports.")
            return sorted_reports
        except Exception as e:
            self.logger.error(f"Failed to sort reports: {e}")
            return []
