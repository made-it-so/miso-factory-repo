import logging
import json
import ollama

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class SimulationAgent:
    """
    Analyzes a project plan to proactively identify potential failures,
    risks, and logical inconsistencies before execution.
    Inspired by the 'Foretell' proactive planning framework.
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ollama_client = ollama.Client()
        self.logger.info("Simulation Agent (Foresight Protocol) initialized.")

    def run_simulation(self, plan):
        """
        Takes a plan, simulates its execution by reasoning about potential
        failure modes, and returns a risk analysis.

        Args:
            plan (dict): A dictionary describing the project plan.

        Returns:
            dict: A dictionary containing the simulation results.
        """
        self.logger.info(f"Running foresight simulation for plan: {plan.get('goal')}")

        system_prompt = """You are a meticulous and pessimistic senior software architect. Your task is to analyze a given project plan and identify potential risks, logical flaws, ambiguities, or future implementation problems. Think step-by-step about what could go wrong.

Return your analysis ONLY as a valid JSON object with two keys:
1. "status": A string, either "PlanOK" if you find no significant risks, or "RisksIdentified" if you find potential issues.
2. "risks": A list of strings, where each string is a specific, actionable risk you have identified. If there are no risks, return an empty list."""

        user_prompt = f"Analyze this project plan:\n\n{json.dumps(plan, indent=2)}"

        try:
            response = self.ollama_client.chat(
                model='llama3',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                format='json'
            )
            
            simulation_result = json.loads(response['message']['content'])
            self.logger.info(f"Simulation complete. Status: {simulation_result.get('status')}. Found {len(simulation_result.get('risks', []))} risks.")
            return simulation_result

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response from LLM during simulation: {e}")
            return {"status": "Error", "risks": ["LLM returned malformed JSON."]}
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during simulation: {e}")
            return {"status": "Error", "risks": [f"An unexpected error occurred: {str(e)}"]}

# Example of how this agent might be called (for testing purposes)
if __name__ == '__main__':
    simulation_agent = SimulationAgent()
    
    test_plan = {
        'goal': 'Create a simple Python web server.',
        'steps': [
            'Create a single file for the server.',
            'Add a route that returns a greeting.'
        ]
    }
    print("--- Running Simulation on Ambiguous Plan ---")
    result = simulation_agent.run_simulation(test_plan)
    print(json.dumps(result, indent=2))
# MISO: Forcing a detectable change.
