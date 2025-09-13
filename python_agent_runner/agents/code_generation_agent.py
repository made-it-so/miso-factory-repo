import logging
import ollama
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class CodeGenerationAgent:
    """
    Generates code for a single file based on a detailed description.
    """
    def __init__(self, model="llama3"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = model
        self.logger.info(f"CodeGenerationAgent initialized with model: {self.model}")

    def _get_language_from_path(self, file_path: str) -> str:
        """Infers the programming language from the file extension."""
        _, ext = os.path.splitext(file_path)
        lang_map = {
            '.py': 'Python', '.js': 'JavaScript', '.html': 'HTML', '.css': 'CSS',
            '.md': 'Markdown', '.json': 'JSON', '.yml': 'YAML', '.sh': 'Bash'
        }
        return lang_map.get(ext.lower(), 'text')

    def _create_generation_prompt(self, file_path: str, file_description: str) -> str:
        """Creates the prompt for the LLM to generate code for a single file."""
        language = self._get_language_from_path(file_path)
        return f"""
        You are an expert programmer specializing in {language}. Your task is to write the complete, clean, and production-ready source code for a single file as described below.

        **File Path:** {file_path}
        **File Description & Requirements:**
        {file_description}

        **IMPORTANT INSTRUCTIONS:**
        1.  Generate the complete and unabridged source code for this single file.
        2.  Adhere to all requirements in the description.
        3.  DO NOT add any explanatory text, comments, or markdown code fences (like ```python) before or after the code.
        4.  Your entire response must be ONLY the raw source code for the specified file.
        """

    def generate_code(self, file_path: str, file_description: str) -> str:
        """
        Generates and returns the code for a single file.
        Returns the generated source code, or None if an error occurred.
        """
        self.logger.info(f"Generating code for: {file_path}")
        prompt = self._create_generation_prompt(file_path, file_description)

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            generated_code = response['message']['content']
            self.logger.info(f"Successfully generated code for {file_path}.")
            return generated_code
        except Exception as e:
            self.logger.error(f"Failed to generate code for {file_path}: {e}")
            return None
