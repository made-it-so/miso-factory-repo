# agents/auditor_agent.py
import html

class AuditorAgent:
    def __init__(self):
        self.version = "v5.0_Production"
        print(f"AuditorAgent Initialized - Version: {self.version}")

    def review_code(self, html_code: str) -> dict:
        # THE FIX: Un-escape HTML entities like '&lt;' back to '<' before analysis.
        unescaped_code = html.unescape(html_code)
        clean_code = unescaped_code.replace('<pre>', '').replace('</pre>', '').lower()

        feedback = []
        if "</head>" not in clean_code:
            feedback.append("Missing closing </head> tag.")
        if "<body>" not in clean_code:
            feedback.append("Missing <body> tag.")
        
        if not feedback:
            return {"status": "PASS", "feedback": "All primary checks passed."}
        else:
            return {"status": "FAIL", "feedback": " ".join(feedback)}
