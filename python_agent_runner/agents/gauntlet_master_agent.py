import logging
import json
import importlib
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class GauntletMasterAgent:
    """
    Orchestrates the evaluation of a 'student' agent against an 'expert' agent.
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("GauntletMasterAgent initialized.")

    def _load_agent_class(self, agent_name: str):
        module_snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', agent_name).lower()
        module_name = f"python_agent_runner.agents.{module_snake_case}"
        try:
            module = importlib.import_module(module_name)
            return getattr(module, agent_name)
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Could not load agent '{agent_name}' from '{module_name}': {e}")
            return None

    def run_gauntlet(self, mip: dict):
        student_class_name = mip.get("student_agent_class")
        curriculum = mip.get("curriculum", [])
        
        if not student_class_name or not curriculum:
            self.logger.error("MIP is missing required fields for Gauntlet validation.")
            return

        self.logger.info(f"--- Starting Gauntlet Validation for: {student_class_name} ---")
        
        StudentAgentClass = self._load_agent_class(student_class_name)
        if not StudentAgentClass: return

        student = StudentAgentClass()
        student_score = 0
        
        for i, task in enumerate(curriculum):
            self.logger.info(f"\nRunning Task {i+1}/{len(curriculum)}...")
            student_result = None

            if "paper" in task:
                self.logger.info(f"Task type: Analysis on '{task['paper'].get('title', 'Untitled')[:40]}...'")
                student_result = student.analyze_paper(task['paper'])
            
            student_pass = student_result and "error" not in student_result
            if student_pass: student_score += 1
            self.logger.info(f"Task {i+1} Result -> Student: {'Pass' if student_pass else 'Fail'}")

        self.logger.info("\n--- Gauntlet Results ---")
        self.logger.info(f"Student Agent Score: {student_score}/{len(curriculum)}")

        if student_score == len(curriculum):
            self.logger.info("Outcome: Student has been successfully validated. ?")
        else:
            self.logger.info("Outcome: Student failed validation.")
