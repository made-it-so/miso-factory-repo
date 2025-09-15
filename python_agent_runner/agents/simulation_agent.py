import logging
import json
import ollama

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class SimulationAgent:
    """
    Analyzes a project plan for risks and scores its overall quality.
    """
    def __init__(self, model="llama3"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = model
        self.logger.info(f"SimulationAgent initialized with model: {self.model}")

    def _create_risk_prompt(self, plan_json_str: str) -> str:
        """Creates the prompt for the LLM to perform risk analysis."""
        return f"""
        You are an expert AI system architect. Perform a "proactive foresight" simulation on the following project plan.
        Analyze the plan for risks, flaws, or missed edge cases.
        You MUST respond with ONLY a single, valid JSON object with "status", "confidence_score", and "risks".
        
        **Project Plan:**
        {plan_json_str}
        """

    def run_simulation(self, plan: dict) -> dict:
        """Runs a risk analysis simulation on a given plan."""
        self.logger.info("Starting risk simulation...")
        plan_json_str = json.dumps(plan, indent=2)
        prompt = self._create_risk_prompt(plan_json_str)
        try:
            response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': prompt}], format='json')
            report = json.loads(response['message']['content'])
            self.logger.info("Risk simulation complete.")
            return report
        except Exception as e:
            self.logger.error(f"Failed during risk simulation: {e}")
            return {"status": "FAIL", "confidence_score": 0.0, "risks": [{"description": "Failed to generate simulation report."}]}

    def _create_scoring_prompt(self, plan_json_str: str) -> str:
        """Creates the prompt for the LLM to score the quality of a plan."""
        return f"""
        You are an expert system architect. Score the quality of the following project plan from 1-100 based on simplicity, scalability, and maintainability.
        You MUST respond with ONLY a single, valid JSON object with "overall_score" and "justification".
        
        **Project Plan:**
        {plan_json_str}
        """

    def score_plan_quality(self, plan: dict) -> dict:
        """Scores the overall quality of a project plan."""
        self.logger.info("Scoring plan quality...")
        plan_json_str = json.dumps(plan, indent=2)
        prompt = self._create_scoring_prompt(plan_json_str)
        try:
            response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': prompt}], format='json')
            score_data = json.loads(response['message']['content'])
            self.logger.info(f"Plan scored successfully: {score_data.get('overall_score')}/100")
            return score_data
        except Exception as e:
            self.logger.error(f"Failed to score plan: {e}")
            return {"overall_score": 0, "justification": "Error during scoring."}
