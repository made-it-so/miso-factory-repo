import logging
import json
import ollama
from .simulation_agent import SimulationAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class PlanningAgent:
    """
    Generates multiple diverse plans and selects the best one after scoring.
    """
    def __init__(self, model="llama3", num_plans=3):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = model
        self.num_plans = num_plans
        self.simulation_agent = SimulationAgent(model=model)
        self.logger.info(f"PlanningAgent (Parallel Thinking) initialized to generate {self.num_plans} plans.")

    def _create_parallel_planning_prompt(self, objective: str) -> str:
        """Creates the prompt for the LLM to generate multiple project plans."""
        return f"""
        You are a committee of expert AI system architects. Your task is to generate {self.num_plans} diverse and high-quality project plans for the given objective.

        **User Objective:**
        {objective}

        **Instructions:**
        1.  Generate a list containing {self.num_plans} completely separate and distinct project plans.
        2.  Each plan must be a complete JSON object, including a project_name, technologies, and a file_structure.
        3.  Provide architectural variety (e.g., single script vs. package, different libraries).
        4.  You MUST respond with ONLY a single, valid JSON object with a single key "plans" which contains the list of plan objects.
        """

    def create_plan(self, objective: str, max_retries=1) -> dict:
        """
        Generates and evaluates multiple plans, returning the best one.
        """
        self.logger.info(f"Starting parallel planning for objective: {objective}")
        prompt = self._create_parallel_planning_prompt(objective)
        
        plans = []
        for attempt in range(max_retries + 1):
            try:
                response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': prompt}], format='json')
                response_data = json.loads(response['message']['content'])
                plans = response_data.get("plans", [])
                if len(plans) == self.num_plans:
                    self.logger.info(f"Successfully generated {len(plans)} initial plans.")
                    break
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1}: Failed to generate or parse plans. Error: {e}")
                if attempt >= max_retries:
                    return {"error": "Failed to generate valid plans after multiple attempts."}
        
        if not plans:
            return {"error": "LLM failed to generate any plans."}

        scored_plans = []
        for i, plan in enumerate(plans):
            self.logger.info(f"Evaluating Plan {i+1}/{len(plans)}: '{plan.get('project_name')}'")
            score_data = self.simulation_agent.score_plan_quality(plan)
            score = score_data.get('overall_score', 0)
            scored_plans.append({"plan": plan, "score": score})

        if not scored_plans:
            return {"error": "Failed to score any generated plans."}

        best_plan_item = max(scored_plans, key=lambda x: x['score'])
        self.logger.info(f"Selected best plan ('{best_plan_item['plan'].get('project_name')}') with a quality score of {best_plan_item['score']}/100.")
        
        return best_plan_item['plan']
