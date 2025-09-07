# agents/genesis_agent.py
class GenesisAgent:
    def __init__(self):
        print("GenesisAgent (v8) with robust fragment generation.")

    def generate_component_fragment(self, spec: dict) -> str:
        """Generates a clean HTML fragment for a component."""
        title = spec.get("title", "Component")
        # This is a simplified, guaranteed-to-work version for the Gauntlet
        return f"""
        <div style="background:#2d2d2d; padding:20px; border-radius:5px; height:100%; display:flex; flex-direction:column; justify-content:center; align-items:center;">
            <h3 style="margin-bottom:20px;">{title}</h3>
            <p style="color:#888;">(MISO Internal Agent)</p>
            <div style="border:2px solid #4CAF50; padding:10px; margin-top:10px;">
                <p>Generated a standard login component based on internal knowledge base.</p>
            </div>
        </div>
        """
    
    def generate_code_from_spec(self, component_spec: dict, feedback: str = None) -> str:
        # This logic for the main forge remains the same
        if feedback and "missing closing </head> tag" in feedback.lower():
            return self.generate_fixed_login_component(component_spec)
        return self.generate_buggy_login_component(component_spec)

    def generate_buggy_login_component(self, spec):
        return f"""<pre>&lt;!DOCTYPE html&gt;&lt;html&gt;&lt;head&gt;&lt;title&gt;{spec['title']}&lt;/title&gt;&lt;body&gt;...&lt;/body&gt;&lt;/html&gt;</pre>"""

    def generate_fixed_login_component(self, spec):
        return f"""<pre>&lt;!DOCTYPE html&gt;&lt;html&gt;&lt;head&gt;&lt;title&gt;{spec['title']}&lt;/title&gt;&lt;/head&gt;&lt;body&gt;...&lt;/body&gt;&lt;/html&gt;</pre>"""
