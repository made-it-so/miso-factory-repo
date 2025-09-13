import logging
import ollama
import subprocess
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class DebuggingAgent:
    """
    Analyzes a codebase for errors and attempts to fix them using an LLM within a verification loop.
    """
    def __init__(self, model="llama3", max_attempts=3):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = model
        self.max_attempts = max_attempts
        self.logger.info(f"DebuggingAgent initialized with model: {self.model}")

    def _run_linter(self, file_path: str) -> str:
        """Runs pylint on a file and returns a string of errors."""
        self.logger.info(f"Running linter on {file_path}...")
        try:
            result = subprocess.run(
                ['pylint', file_path, '--exit-zero'],
                capture_output=True, text=True, check=False
            )
            errors = [line for line in result.stdout.splitlines() if 'E:' in line or 'F:' in line]
            if not errors:
                self.logger.info(f"{file_path} is clean.")
                return ""
            return "\n".join(errors)
        except FileNotFoundError:
            self.logger.error("`pylint` command not found. Please ensure it is installed.")
            return "FATAL: pylint not found."
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while running linter: {e}")
            return f"FATAL: Linter execution failed: {e}"

    def _create_debugging_prompt(self, code: str, errors: str) -> str:
        """Creates a prompt for the LLM to debug the code."""
        return f"""
        You are an expert Python programmer and debugger. Your task is to fix the errors in the following Python code.

        **Source Code:**
        ```python
        {code}
        ```

        **Pylint Errors:**
        ```
        {errors}
        ```

        **Instructions:**
        1.  Analyze the provided Pylint errors and the source code.
        2.  Correct the code to fix all the identified errors.
        3.  Ensure the corrected code is clean, syntactically correct, and maintains the original functionality.
        4.  Your entire response must be ONLY the raw, corrected, and complete Python source code for the file. Do not add any explanations or markdown.
        """

    def _debug_file(self, file_path: str) -> bool:
        """Runs the lint-repair-verify loop for a single file."""
        for attempt in range(self.max_attempts):
            self.logger.info(f"Debugging attempt {attempt + 1}/{self.max_attempts} for {file_path}")
            errors = self._run_linter(file_path)
            if not errors:
                return True
            if "FATAL" in errors:
                return False

            self.logger.warning(f"Found errors in {file_path}:\n{errors}")
            with open(file_path, 'r', encoding='utf-8') as f:
                current_code = f.read()
            
            prompt = self._create_debugging_prompt(current_code, errors)
            
            try:
                self.logger.info("Asking LLM for a fix...")
                response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': prompt}])
                fixed_code = response['message']['content'].strip().replace("```python", "").replace("```", "")
                
                with open(file_path, 'w', encoding='utf--8') as f:
                    f.write(fixed_code)
                self.logger.info("Applied LLM's fix. Re-verifying...")
            except Exception as e:
                self.logger.error(f"Failed to get or apply fix from LLM: {e}")
                return False
        
        final_errors = self._run_linter(file_path)
        if not final_errors:
            self.logger.info(f"Successfully debugged {file_path}.")
            return True
        else:
            self.logger.error(f"Failed to debug {file_path} after {self.max_attempts} attempts. Final errors:\n{final_errors}")
            return False

    def debug_codebase(self, project_path: str) -> bool:
        """Finds all Python files in a directory and attempts to debug them."""
        self.logger.info(f"Starting to debug codebase at: {project_path}")
        all_files_ok = True
        for root, _, files in os.walk(project_path):
            for file in files:
                if file.endswith('.py'):
                    if not self._debug_file(os.path.join(root, file)):
                        all_files_ok = False
        
        if all_files_ok:
            self.logger.info("Codebase debugging completed successfully.")
        else:
            self.logger.warning("Codebase debugging completed, but one or more files could not be fixed.")

        return all_files_ok
