import logging
import ollama
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class CodeGenerationAgent:
    """
    Generates code for a single file based on a detailed description and project context.
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

    def _create_generation_prompt(self, file_path: str, file_description: str, project_context: dict) -> str:
        """Creates the prompt for the LLM to generate code for a single file."""
        language = self._get_language_from_path(file_path)
        
        context_summary = "\n".join(
            f"--- File: {path} ---\n{summary}\n"
            for path, summary in project_context.items()
        )

        return f"""
        You are an expert programmer specializing in {language}. Your task is to write the complete source code for a single file within a larger project.

        **Project Context (Summaries of other files generated so far):**
        ```
        {context_summary if context_summary else "No other files have been generated yet."}
        ```

        **Current File to Generate:**
        - **File Path:** `{file_path}`
        - **Description & Requirements:** {file_description}

        **IMPORTANT INSTRUCTIONS:**
        1.  Use the "Project Context" to understand how this file should interact with other parts of the project. Include correct import statements or references as needed.
        2.  Generate the complete and unabridged source code for **only the file specified**.
        3.  Your entire response must be ONLY the raw source code. Do not add any explanatory text, comments, or markdown fences.
        """

    def generate_code(self, file_path: str, file_description: str, project_context: dict) -> str:
        """
        Generates and returns the code for a single file, using project context.
        Returns the generated source code, or None if an error occurred.
        """
        self.logger.info(f"Generating code for: {file_path} with context...")
        prompt = self._create_generation_prompt(file_path, file_description, project_context)

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            generated_code = response['message']['content'].strip().replace("```", "")
            self.logger.info(f"Successfully generated code for {file_path}.")
            return generated_code
        except Exception as e:
            self.logger.error(f"Failed to generate code for {file_path}: {e}")
            return None
