import logging
import subprocess
import json
import os
import ollama
from .code_generation_agent import CodeGenerationAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class SecurityAgent:
    """
    Performs defensive (static analysis) and offensive (red team) security tests.
    """
    def __init__(self, model="llama3"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = model
        self.code_gen_agent = CodeGenerationAgent(model=model)
        self.logger.info("SecurityAgent initialized.")

    def static_scan(self, project_path: str) -> dict:
        """Runs a Bandit scan on a directory and returns a structured report."""
        # This is the original scan_codebase method, renamed for clarity
        self.logger.info(f"Starting static security scan on codebase at: {project_path}")
        command = ['bandit', '-r', project_path, '-f', 'json']
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            if not result.stdout or not result.stdout.strip():
                return {"status": "SECURE", "issues": []}
            report = json.loads(result.stdout)
            issues = report.get('results', [])
            if not issues:
                return {"status": "SECURE", "issues": []}
            else:
                simplified_issues = [{"file": i.get("filename"), "issue": i.get("issue_text"), "severity": i.get("issue_severity"), "line": i.get("line_number")} for i in issues]
                return {"status": "INSECURE", "issues": simplified_issues}
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during static scan: {e}")
            return {"status": "FAIL", "reason": str(e)}

    def _brainstorm_vulnerabilities(self, codebase: str) -> str:
        """Uses an LLM to brainstorm potential logical vulnerabilities."""
        self.logger.info("Brainstorming potential vulnerabilities...")
        prompt = f"""
        You are a senior penetration tester. Analyze the following codebase for potential logical vulnerabilities, not just simple syntax errors.
        Focus on issues like insecure direct object references, authentication bypass, or race conditions.

        **Codebase:**
        ```
        {codebase[:8000]}
        ```

        **Instructions:**
        Identify the single most likely and critical logical vulnerability. Describe it in one clear sentence.
        Respond with ONLY the one-sentence description.
        """
        response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content'].strip()

    def run_red_team_test(self, project_path: str) -> dict:
        """Performs a red team exercise on a generated project."""
        self.logger.info(f"--- Starting Red Team Test for {project_path} ---")
        
        # 1. Ingest Codebase
        codebase_content = ""
        for root, _, files in os.walk(project_path):
            for file in files:
                if file.endswith('.py') or file.endswith('.html') or file.endswith('.js'):
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            codebase_content += f"--- FILE: {file} ---\n{f.read()}\n\n"
                    except: continue

        if not codebase_content: return {"status": "FAIL", "reason": "No code found to analyze."}

        # 2. Brainstorm Vulnerability
        vulnerability_hypothesis = self._brainstorm_vulnerabilities(codebase_content)
        self.logger.info(f"Identified top vulnerability hypothesis: {vulnerability_hypothesis}")

        # 3. Generate Exploit Script
        self.logger.info("Tasking CodeGenerationAgent to write an exploit script...")
        exploit_description = f"Write a Python script using the 'requests' and 'unittest' libraries to test for the following vulnerability in a locally running Flask app: {vulnerability_hypothesis}. The script should print 'SUCCESS' if the exploit works, and 'FAILURE' otherwise."
        exploit_script = self.code_gen_agent.generate_code("exploit.py", exploit_description, {})
        
        if not exploit_script:
            return {"status": "FAIL", "reason": "Failed to generate exploit script."}

        # 4. Sandbox Execution (Simulated) & 5. Reporting
        self.logger.warning("Sandbox execution environment not yet implemented. Skipping actual exploit run.")
        report = {
            "status": "COMPLETE",
            "vulnerability_found": vulnerability_hypothesis,
            "generated_exploit_script": exploit_script,
            "result": "NOT_EXECUTED (Sandbox required)"
        }
        return report
