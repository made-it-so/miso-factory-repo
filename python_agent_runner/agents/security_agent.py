import logging
import subprocess
import json
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class SecurityAgent:
    """
    Scans a codebase for security vulnerabilities using the Bandit tool.
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("SecurityAgent initialized.")

    def scan_codebase(self, project_path: str) -> dict:
        """
        Runs a Bandit scan on a directory and returns a structured report.
        """
        self.logger.info(f"Starting security scan on codebase at: {project_path}")
        command = ['bandit', '-r', project_path, '-f', 'json']

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False
            )
            
            # THE FIX: Handle cases where Bandit finds no issues and returns empty stdout
            if not result.stdout or not result.stdout.strip():
                self.logger.info("Bandit scan produced no output, indicating no issues found.")
                return {"status": "SECURE", "issues": []}

            report = json.loads(result.stdout)
            issues = report.get('results', [])
            
            if not issues:
                self.logger.info("Bandit scan completed. No security issues found.")
                return {"status": "SECURE", "issues": []}
            else:
                self.logger.warning(f"Bandit scan found {len(issues)} potential security issues.")
                simplified_issues = [
                    {
                        "file": issue.get("filename"),
                        "issue": issue.get("issue_text"),
                        "severity": issue.get("issue_severity"),
                        "line": issue.get("line_number")
                    } for issue in issues
                ]
                return {"status": "INSECURE", "issues": simplified_issues}

        except FileNotFoundError:
            self.logger.error("`bandit` command not found. Please run `pip install bandit`.")
            return {"status": "FAIL", "reason": "Bandit not found."}
        except json.JSONDecodeError:
            self.logger.error(f"Failed to decode JSON from Bandit output. Raw output: {result.stdout}")
            return {"status": "FAIL", "reason": "Failed to parse Bandit report."}
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during security scan: {e}")
            return {"status": "FAIL", "reason": str(e)}
