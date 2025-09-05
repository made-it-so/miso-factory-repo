import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class DiscoveryAgent:
    def __init__(self):
        self.analysis_model = "gpt-4o"
        print(f"Discovery Agent initialized with model: {self.analysis_model}")

    def start_interview(self, idea_description):
        """
        Analyzes a user's app idea to generate a clarity score and metaphor.
        """
        print(f"Discovery Agent: Analyzing app idea...")

        system_prompt = """You are a world-class business analyst and product manager.
        A user will provide a description of a software application they want to build.
        Your task is to analyze this idea and return a JSON object with two keys:
        1. "clarity_score": An integer between 0 and 100 representing how well-defined and clear the idea is. 100 is perfectly clear.
        2. "metaphor": A simple, intuitive metaphor to help the user understand the proposed application (e.g., "A digital swiss army knife for sales teams")."""

        user_prompt = f"Analyze the following application idea:\n\n'{idea_description}'"

        try:
            response = openai.chat.completions.create(
                model=self.analysis_model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            analysis = json.loads(response.choices[0].message.content)
            print("Discovery Agent: Analysis complete.")
            return analysis

        except Exception as e:
            print(f"Discovery Agent Error: {e}")
            return {"error": "Failed to analyze the application idea."}
