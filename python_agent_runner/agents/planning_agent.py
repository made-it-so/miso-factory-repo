import logging
import json
import ollama

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class PlanningAgent:
    """
    Takes a high-level objective and creates a detailed, structured plan in JSON format.
    """
    def __init__(self, model="llama3"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = model
        self.logger.info(f"PlanningAgent initialized with model: {self.model}")

    def _create_planning_prompt(self, objective: str) -> str:
        """Creates the prompt for the LLM to generate a project plan."""
        return f"""
        You are an expert AI project planner. Your task is to take a user's objective and break it down into a detailed, step-by-step technical plan.

        **User Objective:**
        {objective}

        **Instructions:**
        1.  Think step-by-step. Decompose the objective into a sequence of clear, actionable tasks.
        2.  For each task, specify the technologies to be used (e.g., Python, Flask, React, Docker).
        3.  Define the file structure and list the key files to be created.
        4.  Describe the core logic or components for each file.
        5.  You MUST respond with ONLY a single, valid JSON object.

        **JSON Output Format:**
        {{
          "project_name": "<string>",
          "technologies": ["<string>"],
          "file_structure": {{
            "directory_name": {{
              "file_name.ext": "Description of file's purpose and core logic."
            }}
          }},
          "execution_steps": [
            {{
              "step": <int>,
              "description": "<string>",
              "command": "<string>"
            }}
          ]
        }}
        """

    def create_plan(self, objective: str) -> dict:
        """
        Generates a structured plan from a user objective.

        Args:
            objective (str): The high-level user request.

        Returns:
            dict: A dictionary containing the structured project plan.
        """
        self.logger.info(f"Creating a new plan for objective: {objective}")
        prompt = self._create_planning_prompt(objective)

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                format='json'
            )
            plan_str = response['message']['content']
            plan = json.loads(plan_str)
            self.logger.info("Successfully generated project plan.")
            return plan
        except Exception as e:
            self.logger.error(f"Failed to create project plan: {e}")
            return { "error": "Failed to generate plan.", "details": str(e) }
