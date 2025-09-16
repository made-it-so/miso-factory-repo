# This module will define the individual agents in the MISO Genesis Pipeline.

class EthicsAgent:
    """
    Analyzes a prompt to ensure it aligns with MISO's ethical guidelines.
    """
    def evaluate(self, prompt: str) -> (bool, str):
        # In a real implementation, this would involve a call to a sophisticated model.
        # For now, it performs a basic keyword check and returns a rationale.
        print("ETHICS_AGENT: Evaluating prompt...")
        
        # Simple check for harmful content placeholder
        forbidden_keywords = ["harmful", "illegal", "malicious"]
        if any(keyword in prompt.lower() for keyword in forbidden_keywords):
            rationale = "Evaluation failed: Prompt contains potentially harmful keywords."
            print(f"ETHICS_AGENT: {rationale}")
            return False, rationale

        rationale = "Evaluation passed: Prompt is compliant with MISO ethical guidelines."
        print(f"ETHICS_AGENT: {rationale}")
        return True, rationale
