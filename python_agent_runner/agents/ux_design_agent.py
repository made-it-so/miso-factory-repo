# agents/ux_design_agent.py
import json
import os

class UX_Design_Agent:
    def __init__(self):
        # Determine the absolute path to the knowledge base
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.kb_path = os.path.join(base_dir, '..', 'knowledge_base', 'ux_knowledge_base.json')
        print("UX_Design_Agent initialized.")

    def get_design_principles(self, component_name: str) -> list:
        """Reads and returns design principles from the knowledge base."""
        try:
            with open(self.kb_path, 'r') as f:
                kb = json.load(f)
            return kb.get(component_name, {}).get("principles", [])
        except FileNotFoundError:
            print(f"Knowledge base not found at {self.kb_path}")
            return []
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {self.kb_path}")
            return []
            
    def create_component_mockup(self, component_name: str) -> str:
        """Generates a simple HTML mockup for a component."""
        # This function remains for other potential uses
        return f"<h3>Mockup for {component_name}</h3>"
