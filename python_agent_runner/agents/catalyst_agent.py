import logging
import json
import ollama

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class CatalystAgent:
    """Finds novel or synergistic connections between research and MISO's goals."""
    def __init__(self, model="llama3"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = model
        self.logger.info("CatalystAgent initialized.")

    def _create_novelty_prompt(self, paper: dict) -> str:
        return f"""
        You are a creative and lateral-thinking AI Research Strategist for the MISO project.
        Your task is to find novel, non-obvious, or synergistic connections between a research paper and MISO's core objectives.

        **MISO's Core Objectives:** Multi-Agent Systems, Autonomous Code Generation, AI Planning, Self-Improvement Architectures.

        **Paper Title:** {paper.get('title')}
        **Paper Summary:** {paper.get('summary')}

        **Instructions:**
        1.  Think creatively. Could this research, even if from an unrelated field (e.g., biology, economics, art), be metaphorically or structurally applied to improve MISO?
        2.  Provide a novelty score from 1 (no novel connection) to 10 (a groundbreaking, non-obvious connection).
        3.  Provide a brief, one-sentence justification explaining the novel connection.
        4.  You MUST respond with ONLY a single, valid JSON object.

        **JSON Output Format:**
        {{
          "novelty_score": <integer>,
          "justification": "<string>"
        }}
        """

    def find_novelty(self, paper: dict) -> dict:
        """Takes a paper and returns a novelty score and justification."""
        prompt = self._create_novelty_prompt(paper)
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                format='json'
            )
            novelty_data_str = response['message']['content']
            return json.loads(novelty_data_str)
        except Exception as e:
            self.logger.error(f"CatalystAgent failed to find novelty for '{paper.get('title')}': {e}")
            return {"novelty_score": 0, "justification": "Error during novelty analysis."}
