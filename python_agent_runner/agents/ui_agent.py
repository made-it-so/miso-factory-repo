# agents/ui_agent.py
from agents.ux_design_agent import UX_Design_Agent
from agents.genesis_agent import GenesisAgent
# ... (other imports)
from agents.discovery_agent import DiscoveryAgent
from agents.openai_competitor_agent import OpenAICompetitorAgent
import random

class UIAgent:
    def __init__(self, max_retries=1):
        # ... (agent initializations)
        self.genesis_agent = GenesisAgent()
        self.openai_competitor = OpenAICompetitorAgent()
        self.discovery_agent = DiscoveryAgent()
        self.state = "IDLE"
        self.pending_spec = {}
        print("UIAgent (v11.0) with restored command logic.")

    def handle_request(self, user_message: str) -> dict:
        user_message_lower = user_message.lower()

        # State machine for conversational flows
        if self.state == "AWAITING_ANSWERS":
            # ... (unchanged logic for handling answers)
            self.state = "AWAITING_CONFIRMATION"
            # ... return confirmation ...
        elif self.state == "AWAITING_CONFIRMATION":
            # ... (unchanged logic for handling final confirmation)
            self.state = "IDLE"
            # ... return result ...

        # --- COMMAND ROUTING (IDLE STATE) ---
        if "gauntlet" in user_message_lower:
            # Gauntlet logic
            challenge_prompt = "A modern, clean login form component."
            internal_design = self.genesis_agent.generate_component_fragment({"name": "Login Component", "title": "Internal Design"})
            external_design = self.openai_competitor.generate_design(challenge_prompt)
            designs = [internal_design, external_design]; random.shuffle(designs)
            return {"type": "DECISION_REQUEST", "question": "The Gauntlet: Which design is superior?", "options": {"option_a": designs[0], "option_b": designs[1]}}
        
        elif "create a login page" in user_message_lower:
            # RESTORED: Funnel-Down Dialogue logic
            questions = self.discovery_agent.generate_clarifying_questions(user_message_lower)
            self.state = "AWAITING_ANSWERS"
            self.pending_spec = {"name": "Login Component"}
            response_text = "<br>".join(["Before I proceed, please answer these questions:"] + questions)
            return { "type": "STANDARD_RESPONSE", "response": response_text, "blueprint": "<pre>STATUS: Awaiting User Input</pre>", "workspace": "" }

        elif "map out" in user_message_lower:
            # Mermaid map logic
            mermaid_text = "mindmap\n  root((E-Commerce App))\n    User-Facing\n      Homepage\n    Backend Services\n      Authentication"
            return {"type": "STANDARD_RESPONSE", "response": "Generating architecture...", "blueprint": "MERMAID_DATA:" + mermaid_text, "workspace": ""}
        
        else:
            return { "type": "STANDARD_RESPONSE", "response": f"Command not recognized.", "blueprint": "", "workspace": "" }

    # ... (other helper methods like _trigger_colosseum_protocol remain)
