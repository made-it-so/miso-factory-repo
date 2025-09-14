import logging
import json
import ollama
from .catalyst_agent import CatalystAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class TriageAgent:
    """Scores and filters papers based on relevance and novelty."""
    def __init__(self, model="llama3", final_threshold=6.0):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = model
        self.final_threshold = final_threshold
        self.catalyst_agent = CatalystAgent(model=model)
        self.logger.info(f"TriageAgent initialized with final score threshold: {self.final_threshold}")

    def _create_relevance_prompt(self, paper: dict) -> str:
        return f"""
        You are an AI Research Scientist working for the MISO project, an autonomous AI software engineer.
        Your task is to triage a research paper based on its title and summary to determine its relevance to MISO's core objectives.

        **MISO's Core Objectives:**
        - Multi-Agent Systems (MAS)
        - Autonomous Code Generation and Software Engineering
        - AI Planning, Reasoning, and Simulation
        - Autonomous Self-Improvement and Learning Architectures (e.g., The Crucible)
        - Human-AI Interaction and Collaboration

        **Paper Title:** {paper.get('title')}
        **Paper Summary:** {paper.get('summary')}

        **Instructions:**
        1.  Read the title and summary carefully.
        2.  Evaluate how directly the paper's topic applies to MISO's core objectives.
        3.  Provide a relevance score from 1 (not relevant) to 10 (highly relevant and critical).
        4.  Provide a brief, one-sentence justification for your score.
        5.  You MUST respond with ONLY a single, valid JSON object.

        **JSON Output Format:**
        {{
          "relevance_score": <integer between 1 and 10>,
          "justification": "<string>"
        }}
        """

    def _normalize_score(self, score: int) -> float:
        """Normalizes a score to be within the 1-10 range."""
        if score > 10:
            self.logger.warning(f"Received out-of-scale score '{score}'. Normalizing to {score / 10.0}.")
            return score / 10.0
        return float(score)

    def run_triage(self, papers: list) -> list:
        """Takes a list of papers, scores them for relevance AND novelty, and returns a filtered list."""
        self.logger.info(f"Triaging {len(papers)} papers with two-factor analysis...")
        triaged_papers = []

        for i, paper in enumerate(papers):
            self.logger.info(f"Analyzing paper {i + 1}/{len(papers)}: '{paper.get('title')[:50]}...'")
            try:
                # Step 1: Get Relevance Score
                relevance_prompt = self._create_relevance_prompt(paper)
                relevance_response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': relevance_prompt}], format='json')
                relevance_data = json.loads(relevance_response['message']['content'])
                relevance_score = self._normalize_score(relevance_data.get("relevance_score", 0))
                
                # Step 2: Get Novelty Score
                novelty_data = self.catalyst_agent.find_novelty(paper)
                novelty_score = self._normalize_score(novelty_data.get("novelty_score", 0))

                # Step 3: Calculate Final Score
                final_score = (relevance_score * 0.7) + (novelty_score * 0.3)
                
                self.logger.info(f"Scores -> Relevance: {relevance_score:.1f}, Novelty: {novelty_score:.1f}, Final: {final_score:.2f}")

                if final_score >= self.final_threshold:
                    paper['relevance_score'] = relevance_score
                    paper['relevance_justification'] = relevance_data.get("justification")
                    paper['novelty_score'] = novelty_score
                    paper['novelty_justification'] = novelty_data.get("justification")
                    paper['final_score'] = final_score
                    triaged_papers.append(paper)
                    self.logger.info("Paper is RELEVANT. Added to list.")
                else:
                    self.logger.info("Paper is NOT relevant. Discarding.")
            except Exception as e:
                self.logger.error(f"Failed to triage paper '{paper.get('title')}': {e}")
        
        self.logger.info(f"Triage complete. Found {len(triaged_papers)} relevant papers.")
        return triaged_papers
