# agents/discovery_agent.py

class DiscoveryAgent:
    def __init__(self):
        self.version = "v1.0"
        print("DiscoveryAgent Initialized.")

    def generate_clarifying_questions(self, topic: str) -> list:
        """
        Based on a topic, generate a list of questions to refine user intent.
        """
        topic = topic.lower()
        
        # This can be expanded or replaced with an LLM call in the future.
        if "login page" in topic:
            return [
                "Should this form include options for social media sign-in (e.g., Google, Facebook)?",
                "Is two-factor authentication (2FA) required?",
                "What is the desired aesthetic (e.g., minimalist, corporate, dark mode)?",
                "Should it include a 'Remember Me' checkbox?"
            ]
        
        return ["What are the primary goals of this component?"]

