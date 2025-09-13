import logging
import json
import ollama

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class SimulationAgent:
    """
    Analyzes a project plan to identify potential risks and failures before execution.
    """
    def __init__(self, model="llama3"):
        """
        Initializes the SimulationAgent.
        Args:
            model (str): The name of the Ollama model to use for the simulation.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = model
        self.logger.info(f"SimulationAgent initialized with model: {self.model}")

    def _create_simulation_prompt(self, plan_json_str: str) -> str:
        """Creates the detailed prompt for the LLM-based simulation."""
        return f"""
        You are an expert AI system architect and senior software engineer. Your task is to perform a "proactive foresight" simulation on the following project plan.
        Analyze the plan for potential risks, logical flaws, missed edge cases, scalability issues, security vulnerabilities, and maintenance concerns.

        **Project Plan:**
        {plan_json_str}

        **Instructions:**
        1.  Critically evaluate the plan from the perspective of a seasoned architect.
        2.  Identify a list of potential risks, categorizing their severity (LOW, MEDIUM, HIGH, CRITICAL).
        3.  For each risk, provide a concise description and a concrete suggestion for mitigation.
        4.  Based on your analysis, determine an overall status: 'PASS' (no critical/high risks), 'WARNING' (medium/low risks found), or 'FAIL' (at least one critical/high risk).
        5.  Provide a confidence score (0.0 to 1.0) for your overall assessment.
        6.  You MUST respond with ONLY a single, valid JSON object, with no other text before or after it.

        **JSON Output Format:**
        {{
          "status": "PASS | FAIL | WARNING",
          "confidence_score": 0.95,
          "risks": [
            {{
              "risk_id": "R001",
              "description": "API endpoint has no rate-limiting, potential for abuse.",
              "severity": "HIGH",
              "suggestion": "Implement a token bucket rate-limiting strategy."
            }}
          ]
        }}
        """

    def run_simulation(self, plan: dict) -> dict:
        """
        Runs the simulation on a given plan.

        Args:
            plan (dict): A dictionary representing the project plan.

        Returns:
            dict: A dictionary containing the simulation report.
        """
        self.logger.info("Starting simulation...")
        plan_json_str = json.dumps(plan, indent=2)
        prompt = self._create_simulation_prompt(plan_json_str)

        try:
            self.logger.info("Sending plan to LLM for analysis...")
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                format='json'
            )
            
            report_str = response['message']['content']
            self.logger.info("Received raw analysis from LLM.")
            
            report = json.loads(report_str)
            self.logger.info("Simulation complete. Report generated successfully.")
            return report

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON from LLM response: {e} -- Response: {report_str}")
            return {
                "status": "FAIL", "confidence_score": 0.0,
                "risks": [{"risk_id": "E001", "description": "The LLM returned a response that was not valid JSON.", "severity": "CRITICAL", "suggestion": "Check logs for the raw LLM response."}]
            }
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during simulation: {e}")
            return {
                "status": "FAIL", "confidence_score": 0.0,
                "risks": [{"risk_id": "E002", "description": f"An unexpected error occurred: {str(e)}", "severity": "CRITICAL", "suggestion": "Review application logs."}]
            }
