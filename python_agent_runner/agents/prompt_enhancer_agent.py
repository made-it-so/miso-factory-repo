import logging
import ollama

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class PromptEnhancerAgent:
    """
    Takes a raw user objective and refines it into a more detailed and structured prompt.
    """
    def __init__(self, model="llama3"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = model
        self.logger.info(f"PromptEnhancerAgent initialized with model: {self.model}")

    def _create_enhancement_prompt(self, objective: str) -> str:
        """Creates the prompt for the LLM to enhance the user's objective."""
        return f"""
        You are a world-class Solution Architect. Your task is to take a user's brief, potentially vague, project objective and enhance it into a detailed, actionable objective for an AI development team.

        **User's Raw Objective:**
        "{objective}"

        **Instructions:**
        1.  Analyze the user's request and identify any ambiguities.
        2.  Flesh out the objective with common-sense technical requirements and non-functional requirements (e.g., logging, basic error handling, a simple README).
        3.  Suggest a simple, appropriate technology stack if one is not specified.
        4.  Rewrite the objective into a single, clear, and detailed paragraph. The new objective should be a comprehensive but concise mission statement for the AI agents that will build the project.
        5.  Your entire response must be ONLY the new, enhanced objective paragraph. Do not add any conversational text or preambles.
        """

    def enhance_objective(self, raw_objective: str) -> str:
        """
        Takes a raw objective and returns an enhanced version.
        """
        self.logger.info(f"Enhancing raw objective: '{raw_objective[:50]}...'")
        prompt = self._create_enhancement_prompt(raw_objective)

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            enhanced_objective = response['message']['content'].strip()
            self.logger.info("Successfully enhanced objective.")
            return enhanced_objective
        except Exception as e:
            self.logger.error(f"Failed to enhance objective: {e}")
            # Fallback to the original objective if enhancement fails
            return raw_objective
