import logging
import json
import ollama
import chromadb
from .simulation_agent import SimulationAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class PlanningAgent:
    """
    Generates multiple diverse plans, informed by past projects from the Codex,
    and selects the best one after scoring.
    """
    def __init__(self, model="llama3", num_plans=3):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = model
        self.num_plans = num_plans
        self.simulation_agent = SimulationAgent(model=model)
        try:
            self.chroma_client = chromadb.PersistentClient(path="miso_code_db")
            self.code_collection = self.chroma_client.get_collection(name="miso_source_code")
            self.logger.info("Successfully connected to Codex (ChromaDB).")
        except Exception as e:
            self.logger.warning(f"Could not connect to Codex. Proceeding without memory. Error: {e}")
            self.code_collection = None
        self.logger.info(f"PlanningAgent (Parallel Thinking w/ Memory) initialized.")

    def _retrieve_context_from_codex(self, objective: str, n_results=3) -> str:
        """Retrieves relevant code snippets from the Codex."""
        if not self.code_collection:
            return "No historical context available."
        try:
            response = ollama.embeddings(model='mxbai-embed-large', prompt=objective)
            results = self.code_collection.query(query_embeddings=[response["embedding"]], n_results=n_results)
            context_str = "\n---\n".join(results['documents'][0])
            self.logger.info("Successfully retrieved context from Codex.")
            return context_str
        except Exception as e:
            self.logger.error(f"Failed to retrieve context from Codex: {e}")
            return "Error retrieving historical context."

    def _create_parallel_planning_prompt(self, objective: str, context: str) -> str:
        """Creates the prompt for the LLM to generate multiple project plans."""
        return f"""
        You are a committee of expert AI system architects.
        Use the Historical Context as inspiration for creating {self.num_plans} diverse and high-quality project plans for the given objective.

        **Historical Context (Code from similar past projects):**
        ```
        {context}
        ```

        **User Objective:**
        {objective}

        **Instructions:**
        1.  Generate a list containing {self.num_plans} completely separate and distinct project plans.
        2.  Each plan must be a complete JSON object.
        3.  You MUST respond with ONLY a single, valid JSON object with a single key "plans" which contains the list of plan objects.
        """

    def create_plan(self, objective: str, max_retries=1) -> dict:
        """Generates and evaluates multiple plans, returning the best one."""
        self.logger.info(f"Starting memory-enhanced parallel planning for objective: {objective}")
        context = self._retrieve_context_from_codex(objective)
        prompt = self._create_parallel_planning_prompt(objective, context)
        
        plans = []
        for attempt in range(max_retries + 1):
            try:
                response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': prompt}], format='json')
                plans = json.loads(response['message']['content']).get("plans", [])
                if len(plans) > 0:
                    self.logger.info(f"Successfully generated {len(plans)} initial plans.")
                    break
            except Exception as e:
                if attempt >= max_retries:
                    return {"error": "Failed to generate valid plans.", "details": str(e)}
        
        scored_plans = []
        for i, plan in enumerate(plans):
            self.logger.info(f"Evaluating Plan {i+1}/{len(plans)}: '{plan.get('project_name')}'")
            score_data = self.simulation_agent.score_plan_quality(plan)
            scored_plans.append({"plan": plan, "score": score_data.get('overall_score', 0)})

        if not scored_plans:
            return {"error": "Failed to score any generated plans."}

        best_plan_item = max(scored_plans, key=lambda x: x['score'])
        self.logger.info(f"Selected best plan ('{best_plan_item['plan'].get('project_name')}') with score {best_plan_item['score']}/100.")
        
        return best_plan_item['plan']
