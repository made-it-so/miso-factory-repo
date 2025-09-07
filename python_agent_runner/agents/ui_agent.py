# agents/ui_agent.py
from agents.ux_design_agent import UX_Design_Agent
from agents.genesis_agent import GenesisAgent
from agents.auditor_agent import AuditorAgent

class UIAgent:
    def __init__(self, max_retries=1):
        self.ux_agent = UX_Design_Agent()
        self.genesis_agent = GenesisAgent()
        self.auditor_agent = AuditorAgent()
        self.max_retries = max_retries
        print("UIAgent (v6.0) initialized with Mermaid.js capability.")

    def handle_request(self, user_message: str) -> dict:
        user_message_lower = user_message.lower()
        response_text, blueprint_text, workspace_text = "", "", ""

        if "map out" in user_message_lower or "architect" in user_message_lower:
            response_text = "Understood. Generating architecture with Mermaid.js."
            # This is Mermaid.js syntax for a mind map
            mermaid_text = """
mindmap
  root((E-Commerce App))
    User-Facing
      Homepage
      Product Catalog
        Search & Filter
        Product Detail Page
      Shopping Cart
      Checkout Process
    Backend Services
      Authentication
      Order Processing
      Payment Gateway
"""
            blueprint_text = "MERMAID_DATA:" + mermaid_text.strip()
            workspace_text = ""

        elif "login page" in user_message_lower:
            # This logic remains the same
            response_log = ["Acknowledged. Initiating self-correction protocol..."]
            spec = { "name": "Login Component", "title": "User Sign-In" }
            audit_result = {}
            for attempt in range(self.max_retries + 1):
                feedback = audit_result.get('feedback') if attempt > 0 else None
                code = self.genesis_agent.generate_code_from_spec(spec, feedback=feedback)
                audit_result = self.auditor_agent.review_code(code)
                if audit_result.get('status') == 'PASS':
                    workspace_text = code
                    break
            else:
                workspace_text = f"<pre>AUDIT FAILED</pre>"
            response_text = "Login page generated."
            blueprint_text = "<pre>- [x] Login Component (Self-Corrected)</pre>"
        
        else:
            response_text = f"Request received: '{user_message}'"
            blueprint_text = "// Blueprint awaiting instructions."
            workspace_text = ""

        return { "response": response_text, "blueprint": blueprint_text, "workspace": workspace_text }
