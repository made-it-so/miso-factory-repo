import subprocess
import tempfile
import os
import sys
import json

class Gauntlet:
    # CORRECTED: Added max_complexity to the __init__ method
    def __init__(self, min_score=7.0, max_complexity=10):
        self.min_score = min_score
        self.max_complexity = max_complexity
        print(f"Gauntlet initialized. Min pylint score: {self.min_score}, Max complexity: {self.max_complexity}")

    def run_linter_check(self, code_to_test):
        """
        Runs a pylint check on a string of code and returns a pass/fail result.
        """
        print("\n--- The Gauntlet: Linter Check ---")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(code_to_test)
            temp_file_path = temp_file.name
        try:
            command = [sys.executable, '-m', 'pylint', temp_file_path, '--disable=C0114,C0115,C0116', '--output-format=text']
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            score_line = [line for line in result.stdout.split('\n') if 'Your code has been rated at' in line]
            if not score_line:
                return {"passed": False, "score": 0, "details": "Pylint execution error."}
            score = float(score_line[0].split(' at ')[1].split('/')[0])
            if score >= self.min_score:
                return {"passed": True, "score": score, "details": result.stdout}
            else:
                return {"passed": False, "score": score, "details": result.stdout}
        finally:
            os.remove(temp_file_path)

    def run_security_check(self, code_to_test):
        """Runs a bandit security check on the code."""
        print("\n--- The Gauntlet: Security Scan (Bandit) ---")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(code_to_test)
            temp_file_path = temp_file.name
        try:
            command = [sys.executable, '-m', 'bandit', '-f', 'json', temp_file_path]
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            # Bandit exits with a non-zero code if issues are found, so we parse stdout.
            if result.stdout:
                report = json.loads(result.stdout)
                if report['results']:
                    print(f"Result: FAILED - {len(report['results'])} security issues found.")
                    return {"passed": False, "details": json.dumps(report['results'], indent=2)}
            
            print("Result: PASSED - No security issues found.")
            return {"passed": True, "details": "No security issues found."}
        finally:
            os.remove(temp_file_path)

    def run_complexity_check(self, code_to_test):
        """Runs a radon cyclomatic complexity check."""
        print("\n--- The Gauntlet: Complexity Analysis (Radon) ---")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(code_to_test)
            temp_file_path = temp_file.name
        try:
            command = [sys.executable, '-m', 'radon', 'cc', '-s', '-j', temp_file_path]
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            
            if not result.stdout.strip():
                 print("Result: PASSED - Radon produced no output (likely no complex blocks).")
                 return {"passed": True, "details": "No complex blocks found."}

            report = json.loads(result.stdout)
            high_complexity_blocks = []
            for file_report in report.values():
                for block in file_report:
                    if isinstance(block, dict) and block.get('complexity', 0) > self.max_complexity:
                        high_complexity_blocks.append(block)
            
            if high_complexity_blocks:
                print(f"Result: FAILED - Code with complexity > {self.max_complexity} found.")
                return {"passed": False, "details": json.dumps(high_complexity_blocks, indent=2)}
            else:
                print(f"Result: PASSED - All code blocks are within complexity limits.")
                return {"passed": True, "details": "Max complexity found is acceptable."}
        finally:
            os.remove(temp_file_path)

    def run_unit_tests(self, source_code, test_code, filename):
        """
        Runs pytest on the generated source code and test code.
        """
        print("\n--- The Gauntlet: Unit Test Runner ---")
        with tempfile.TemporaryDirectory() as temp_dir:
            # Add an __init__.py to the temp directory to make it a package
            init_path = os.path.join(temp_dir, "__init__.py")
            with open(init_path, "w", encoding="utf-8") as f:
                f.write("")
                
            source_path = os.path.join(temp_dir, filename)
            test_path = os.path.join(temp_dir, f"test_{filename}")

            with open(source_path, "w", encoding="utf-8") as f:
                f.write(source_code)
            with open(test_path, "w", encoding="utf-8") as f:
                f.write(test_code)

            print(f"Running pytest on {test_path}")
            command = [sys.executable, '-m', 'pytest', test_path]
            result = subprocess.run(command, capture_output=True, text=True, check=False, cwd=temp_dir)

            if result.returncode == 0:
                print("Result: PASSED")
                return {"passed": True, "details": result.stdout}
            else:
                print("Result: FAILED")
                return {"passed": False, "details": result.stdout + "\n" + result.stderr}
