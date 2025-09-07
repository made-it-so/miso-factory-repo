# agents/openai_competitor_agent.py
import os
import openai
from dotenv import load_dotenv

class OpenAICompetitorAgent:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("ERROR: OPENAI_API_KEY not found in .env file.")
            self.client = None
        else:
            self.client = openai.OpenAI(api_key=self.api_key)
        print("OpenAI Competitor Agent initialized.")

    def generate_design(self, prompt: str) -> str:
        """Generates an HTML component using the OpenAI API."""
        if not self.client:
            return "<div>OpenAI API key not configured.</div>"
        
        try:
            print("Sending prompt to OpenAI API...")
            completion = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert UI/UX designer. Create a single, self-contained HTML snippet for the requested component. Do not include <!DOCTYPE html>, <html>, <head>, or <body> tags. Use inline CSS for styling."},
                    {"role": "user", "content": prompt}
                ]
            )
            response_content = completion.choices[0].message.content
            print("Received response from OpenAI API.")
            return response_content.strip()
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return f"<div>Error calling OpenAI API: {e}</div>"
