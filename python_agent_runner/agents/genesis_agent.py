# agents/genesis_agent.py

class GenesisAgent:
    """
    A specialist "Execution" agent that writes and corrects code based on
    a specification and audit feedback.
    """
    def __init__(self):
        print("GenesisAgent (v2) initialized.")

    def generate_code_from_spec(self, component_spec: dict, feedback: str = None) -> str:
        """
        Generates or corrects HTML code.
        If feedback is provided, it attempts to fix the code.
        """
        print(f"GenesisAgent received spec: {component_spec['name']}")
        
        if feedback:
            print(f"GenesisAgent received feedback: {feedback}")
            # This is the self-correction logic
            if "Missing closing </head> tag" in feedback:
                print("Correcting missing </head> tag.")
                # Return the fixed version of the code
                return self.generate_fixed_login_component(component_spec)
        
        # On the first attempt, generate code with a deliberate bug
        print("Generating initial version of code (with bug)...")
        return self.generate_buggy_login_component(component_spec)

    def generate_buggy_login_component(self, spec):
        # This version is missing the </head> tag
        html_code = f"""
<!DOCTYPE html><html lang="en"><head>
    <meta charset="UTF-8"><title>Login Page</title>
    <style>
        body {{ font-family: sans-serif; background: #333; color: white; }}
        .login-box {{ border: 1px solid #555; padding: 20px; width: 300px; margin: 50px auto; }}
    </style>
<body>
    <div class="login-box"><h2>{spec['title']}</h2></div>
</body></html>"""
        return f"<pre>{html_code.strip()}</pre>"

    def generate_fixed_login_component(self, spec):
        # This version includes the </head> tag
        html_code = f"""
<!DOCTYPE html><html lang="en"><head>
    <meta charset="UTF-8"><title>Login Page</title>
    <style>
        body {{ font-family: sans-serif; background: #333; color: white; }}
        .login-box {{ border: 1px solid #555; padding: 20px; width: 300px; margin: 50px auto; }}
    </style>
</head>
<body>
    <div class="login-box"><h2>{spec['title']}</h2></div>
</body></html>"""
        return f"<pre>{html_code.strip()}</pre>"
