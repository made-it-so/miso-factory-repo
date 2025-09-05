import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class LegacyModernizationAgent:
    def __init__(self):
        self.analysis_model = "gpt-4o"
        print(f"Legacy Modernization Agent initialized with model: {self.analysis_model}")

    def create_blueprint(self, source_code, source_language="COBOL"):
        """
        Analyzes legacy code and generates a language-agnostic blueprint.
        """
        print(f"\n--- Legacy Modernization Agent --- \nAnalyzing {source_language} source code...")

        system_prompt = f"""You are an expert software architect specializing in legacy system modernization.
        You will be given a block of source code from an old language ({source_language}).
        Your task is to reverse-engineer its functionality and create a detailed, language-agnostic 'Business Logic Blueprint' in a structured format.
        This blueprint must identify all data structures, inputs, outputs, and the core business rules and calculations.
        Do not write any code, only describe the logic in plain English and structured text."""

        user_prompt = f"Source Code:\n`cobol\n{source_code}\n`"

        try:
            response = openai.chat.completions.create(
                model=self.analysis_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            blueprint = response.choices[0].message.content
            print("Business Logic Blueprint generated successfully.")
            return blueprint
            
        except Exception as e:
            print(f"Legacy Modernization Agent Error: {e}")
            return f"# FAILED TO GENERATE BLUEPRINT: {e}"
