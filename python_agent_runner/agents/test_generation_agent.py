import openai
import os
import re
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class TestGenerationAgent:
    def __init__(self):
        self.generation_model = "gpt-4o"
        print(f"Test Generation Agent initialized with model: {self.generation_model}")

    def generate_tests(self, source_code, filename):
        """
        Analyzes a block of Python code and generates pytest unit tests for it.
        """
        print(f"\n--- Test Generation Agent --- \nGenerating tests for: {filename}\n---------------------------")

        system_prompt = """You are an expert-level QA engineer specializing in automated testing.
        Your task is to receive a Python file's content and filename, and write comprehensive unit tests for it using the pytest framework.
        You must identify edge cases, normal cases, and error conditions. Aim for high test coverage.
        Return only the new, complete, and syntactically correct Python code for the test file.
        Do not include any explanations, markdown formatting, or any text other than the code itself."""

        user_prompt = f"Original Filename: '{filename}'\n\nSource Code:\n`python\n{source_code}\n`"

        try:
            response = openai.chat.completions.create(
                model=self.generation_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            raw_response = response.choices[0].message.content
            
            code_match = re.search(r"`python\n(.*?)\n`", raw_response, re.DOTALL)
            if code_match:
                new_code = code_match.group(1).strip()
            else:
                new_code = raw_response.strip()

            print("Test Generation Agent: Tests generated successfully.")
            return new_code
            
        except Exception as e:
            print(f"Test Generation Agent Error: {e}")
            return f"# FAILED TO GENERATE TESTS: {e}"
