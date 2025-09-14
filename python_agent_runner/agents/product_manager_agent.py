import logging
import json
import ollama

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class ProductManagerAgent:
    """
    Manages the MISO Improvement Proposal (MIP) backlog by estimating effort
    and prioritizing based on a value-vs-effort calculation.
    """
    def __init__(self, model="llama3"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = model
        self.logger.info("ProductManagerAgent initialized.")

    def _create_effort_estimation_prompt(self, proposal: dict) -> str:
        """Creates a prompt to estimate the development effort for a proposal."""
        title = proposal.get('paper_title', 'N/A')
        application = proposal.get('application_to_miso', 'N/A')
        plan = proposal.get('high_level_implementation_plan', [])
        
        return f"""
        You are a senior engineering manager. Your task is to estimate the development effort for the following MISO Improvement Proposal.

        **Proposal Title:** {title}
        **Proposed Application:** {application}
        **Implementation Plan:** {json.dumps(plan, indent=2)}

        **Instructions:**
        Estimate the effort required on a simple scale: Small, Medium, Large, Extra-Large.
        Consider the complexity, number of agents affected, and potential for unforeseen issues.
        You MUST respond with ONLY a single, valid JSON object.

        **JSON Output Format:**
        {{
          "effort_estimate": "Small | Medium | Large | Extra-Large",
          "justification": "A brief explanation for your estimate."
        }}
        """

    def process_backlog(self, backlog: list) -> list:
        """
        Takes a backlog of MIPs, estimates effort for each, and re-prioritizes.
        """
        self.logger.info(f"Processing backlog with {len(backlog)} proposals...")
        effort_map = {"Small": 1, "Medium": 3, "Large": 5, "Extra-Large": 8}
        
        enriched_backlog = []
        for proposal in backlog:
            # Add a placeholder paper_title for consistent access
            if "title" in proposal and "paper_title" not in proposal:
                proposal["paper_title"] = proposal["title"]

            prompt = self._create_effort_estimation_prompt(proposal)
            try:
                response = ollama.chat(
                    model=self.model,
                    messages=[{'role': 'user', 'content': prompt}],
                    format='json'
                )
                effort_data = json.loads(response['message']['content'])

                proposal['effort_estimate'] = effort_data.get('effort_estimate', 'Medium')
                impact = proposal.get('impact_score', 0)
                effort = effort_map.get(proposal['effort_estimate'], 3)
                
                proposal['priority_score'] = (impact / effort) if effort > 0 else 0
                enriched_backlog.append(proposal)
                self.logger.info(f"Assessed '{proposal.get('paper_title')[:30]}...': Impact={impact}, Effort={proposal['effort_estimate']}, Priority={proposal['priority_score']:.2f}")

            except Exception as e:
                self.logger.error(f"Failed to estimate effort for proposal '{proposal.get('paper_title')}': {e}")
        
        prioritized_backlog = sorted(
            enriched_backlog,
            key=lambda p: p.get('priority_score', 0),
            reverse=True
        )
        
        self.logger.info("Successfully re-prioritized backlog.")
        return prioritized_backlog
