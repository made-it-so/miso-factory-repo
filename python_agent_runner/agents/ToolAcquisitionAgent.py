import os
import logging
import subprocess
import sys
import ast
import json
from urllib.parse import urlparse
import ollama

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class ToolAcquisitionAgent:
    """
    Orchestrates the conversion of a code repository into validated, executable tools for MISO.
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.base_dir = "research_subjects"
        os.makedirs(self.base_dir, exist_ok=True)
        self.ollama_client = ollama.Client()
        self.logger.info("Tool Acquisition Agent initialized.")

    def _clone_repository(self, github_url):
        try:
            repo_name = os.path.splitext(os.path.basename(urlparse(github_url).path))[0]
            clone_dir = os.path.join(self.base_dir, repo_name)
            if os.path.isdir(clone_dir):
                self.logger.info(f"Repository '{repo_name}' already exists. Using existing directory.")
                return clone_dir
            self.logger.info(f"Cloning '{github_url}' into '{clone_dir}'...")
            subprocess.run(["git", "clone", github_url, clone_dir], capture_output=True, text=True, check=True, encoding='utf-8')
            return clone_dir
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to clone repository: {e.stderr}")
            return None

    def _analyze_dependencies(self, repo_path):
        requirements_path = os.path.join(repo_path, 'requirements.txt')
        if not os.path.exists(requirements_path): return []
        try:
            with open(requirements_path, 'r', encoding='utf-8') as f: lines = f.readlines()
            return [line.strip() for line in lines if line.strip() and not line.startswith('#')]
        except Exception as e:
            self.logger.error(f"Error parsing requirements.txt: {e}")
            return []

    def _setup_environment(self, repo_path, dependencies):
        venv_path = os.path.join(repo_path, ".venv")
        pip_executable = os.path.join(venv_path, 'Scripts', 'pip.exe') if sys.platform == "win32" else os.path.join(venv_path, 'bin', 'pip')
        python_executable = os.path.join(venv_path, 'Scripts', 'python.exe') if sys.platform == "win32" else os.path.join(venv_path, 'bin', 'python')
        try:
            if not os.path.isdir(venv_path):
                subprocess.run([sys.executable, "-m", "venv", venv_path], check=True, capture_output=True, text=True, encoding='utf-8')
            # Install pytest and any other dependencies
            deps_to_install = ["pytest"] + dependencies
            self.logger.info(f"Installing {len(deps_to_install)} packages...")
            subprocess.run([pip_executable, "install"] + deps_to_install, check=True, capture_output=True, text=True, encoding='utf-8')
            self.logger.info("Environment is ready.")
            return "success", python_executable
        except Exception as e:
            self.logger.error(f"Failed to set up environment: {e}")
            return "failure", None

    def _scan_for_python_files(self, repo_path):
        python_files, venv_path = [], os.path.join(repo_path, ".venv")
        for root, _, files in os.walk(repo_path):
            if os.path.commonpath([root, venv_path]) == venv_path: continue
            for file in files:
                if file.endswith(".py"): python_files.append(os.path.join(root, file))
        return python_files

    def _parse_python_files_ast(self, source_files):
        parsed_structure = {}
        for file_path in source_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
                tree = ast.parse(content)
                functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                parsed_functions = [{"name": func.name, "args": [a.arg for a in func.args.args], "docstring": ast.get_docstring(func) or ""} for func in functions]
                if parsed_functions: parsed_structure[file_path] = parsed_functions
            except Exception as e:
                self.logger.warning(f"Could not parse AST for file {file_path}: {e}")
        return parsed_structure

    def _evaluate_functions_with_llm(self, code_structure):
        self.logger.info("Evaluating function candidates with LLM...")
        # For brevity, this part is mocked. In a real scenario, it would call the LLM.
        mock_candidates = {}
        for file, functions in code_structure.items():
            if 'cli' in file or 'app' in file or 'main' in file: # Heuristic for finding key files
                selected_funcs = [f for f in functions if not f['name'].startswith('_') and f['args']]
                if selected_funcs:
                    mock_candidates[file] = selected_funcs
        self.logger.info(f"LLM evaluation complete. Selected {sum(len(v) for v in mock_candidates.values())} candidates.")
        return mock_candidates

    def _execute_code(self, python_interpreter, code_to_run, working_dir):
        """ Executes a string of Python code in a specified working directory. """
        self.logger.info(f"Executing code with interpreter: {python_interpreter}")
        try:
            result = subprocess.run(
                [python_interpreter, "-c", code_to_run],
                capture_output=True, text=True, check=True, encoding='utf-8', timeout=120, cwd=working_dir
            )
            return "success", result.stdout
        except subprocess.CalledProcessError as e:
            return "failure", e.stderr
        except Exception as e:
            return "failure", str(e)

    def _generate_and_run_tests(self, python_interpreter, repo_path, tool_candidates):
        self.logger.info("Generating and running tests for tool candidates...")
        test_results = {}
        system_prompt = """You are a senior Python QA engineer. Your task is to write a single, simple pytest test for a given function.

Rules:
- The test must be self-contained in a single code block.
- The test must import the necessary function from its module.
- The test should make a simple, valid call to the function and assert a reasonable expectation.
- DO NOT use any external files or network access. Use only simple, inline mock data.
- Your response must be ONLY the Python code inside a `python ... ` block."""

        for file_path, functions in tool_candidates.items():
            module_path = os.path.relpath(file_path, repo_path).replace(os.sep, '.').replace('.py', '')
            for func in functions:
                user_prompt = f"Write a simple pytest test for the function {func['name']} from module {module_path}.\n\nFunction details:\n- Name: {func['name']}\n- Args: {func['args']}\n- Docstring: {func['docstring']}"
                try:
                    response = self.ollama_client.chat(model='llama3', messages=[{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': user_prompt}])
                    test_code = response['message']['content'].strip().replace("`python", "").replace("`", "")
                    
                    test_file_path = os.path.join(repo_path, "test_miso_generated.py")
                    with open(test_file_path, "w", encoding="utf-8") as f: f.write(test_code)

                    # Execute the test
                    status, output = self._execute_code(python_interpreter, f"import pytest; pytest.main(['{test_file_path}'])", repo_path)
                    test_results[f"{module_path}.{func['name']}"] = {"status": status, "output": output.strip()}
                    os.remove(test_file_path)

                except Exception as e:
                    self.logger.error(f"Failed to generate or run test for {func['name']}: {e}")
                    test_results[f"{module_path}.{func['name']}"] = {"status": "failure", "output": str(e)}
        return test_results

    def acquire_tool_from_repository(self, github_url):
        """ Main entry point for the tool acquisition process. """
        self.logger.info(f"--- Starting Full Tool Acquisition and Validation for {github_url} ---")
        
        clone_dir = self._clone_repository(github_url)
        if not clone_dir: return {"status": "Failed", "message": "Could not clone repository."}

        dependencies = self._analyze_dependencies(clone_dir)
        env_status, python_exe = self._setup_environment(clone_dir, dependencies)
        if env_status == "failure": return {"status": "Failed", "message": "Could not set up environment."}

        source_files = self._scan_for_python_files(clone_dir)
        code_structure = self._parse_python_files_ast(source_files)
        tool_candidates = self._evaluate_functions_with_llm(code_structure)
        
        if not tool_candidates:
            return {"status": "Completed", "message": "No suitable tool candidates were identified."}

        test_results = self._generate_and_run_tests(python_exe, clone_dir, tool_candidates)
        
        successful_tools = {k: v for k, v in test_results.items() if v['status'] == 'success'}

        status_report = {
            "status": "Acquisition Complete",
            "message": f"Validated {len(successful_tools)} out of {len(test_results)} candidate tools.",
            "repository_url": github_url,
            "validated_tools": list(successful_tools.keys()),
            "full_test_results": test_results
        }
        
        self.logger.info(f"--- Tool Acquisition Finished ---")
        return status_report

# Example of how this agent might be called (for testing purposes)
if __name__ == '__main__':
    acquisition_agent = ToolAcquisitionAgent()
    repo_url = "https://github.com/pallets/flask"
    result = acquisition_agent.acquire_tool_from_repository(repo_url)
    print(json.dumps(result, indent=2))
