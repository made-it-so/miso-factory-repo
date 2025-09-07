# agents/auditor_agent.py

class AuditorAgent:
    """
    A specialist "Execution" agent that reviews and validates the output
    of other agents, providing specific feedback for correction.
    """
    def __init__(self):
        print("AuditorAgent (v2) initialized.")

    def review_code(self, html_code: str) -> dict:
        """
        Performs a quality check on a string of HTML code.
        """
        print("AuditorAgent is reviewing generated code...")
        
        feedback = []
        errors = 0

        if not html_code or not html_code.strip():
            errors += 1
            feedback.append("Code is empty.")
        
        # Add a more specific check
        if "</head>" not in html_code.lower():
            errors += 1
            feedback.append("Missing closing </head> tag.")

        if "<body>" not in html_code.lower():
            errors += 1
            feedback.append("Missing <body> tag.")

        if errors == 0:
            return {
                "status": "PASS",
                "feedback": "All primary checks passed."
            }
        else:
            return {
                "status": "FAIL",
                "feedback": " ".join(feedback)
            }
