# python_agent_runner/agents/genesis_agent.py
import os
import ollama
from .gauntlet_agent import GauntletAgent # Import the new agent

class GenesisAgent:
    def __init__(self):
        self.gauntlet_agent = GauntletAgent() # Create an instance of the GauntletAgent

    def create_website(self, brief):
        # Step 1: Create the first draft of the prompt
        draft_prompt = f"Create a complete, single-file HTML website based on this brief: {brief}"
        domain = brief.get('domain', 'general web design') # Get the domain from the brief

        # Step 2: Send the draft prompt to the Gauntlet for refinement
        refined_prompt = self.gauntlet_agent.refine_prompt(draft_prompt, domain)

        # Step 3: Use the refined prompt to generate the final product
        try:
            print("GenesisAgent: Sending refined prompt to LLM...")
            response = ollama.chat(
                model='llama3',
                messages=[{'role': 'user', 'content': refined_prompt}],
            )
            html_code = response['message']['content']
            # ... (rest of the file saving logic remains the same)
            
            return {"status": "Success", "preview_url": "/static/output/output.html"}
        except Exception as e:
            return {"status": f"Error: {e}", "preview_url": None}
