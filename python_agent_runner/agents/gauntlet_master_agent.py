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
        """Dynamically loads an agent class from its module name."""
        # Convert PascalCase (e.g., PlanningAgent) to snake_case (e.g., planning_agent)
        module_snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', agent_name).lower()
        module_name = f"python_agent_runner.agents.{module_snake_case}"
        class_name = agent_name
        try:
            module = importlib.import_module(module_name)
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Could not load agent '{class_name}' from '{module_name}': {e}")
            return None

    def run_gauntlet(self, mip: dict):
        """
        Runs the evaluation based on a MISO Improvement Proposal (MIP).
        """
        expert_class_name = mip.get("expert_agent_class")
        student_class_name = mip.get("student_agent_class")
        curriculum = mip.get("curriculum", [])
        
        if not expert_class_name or not student_class_name or not curriculum:
            self.logger.error("MIP is missing required fields.")
            return

        self.logger.info(f"--- Starting Gauntlet for: {expert_class_name} vs {student_class_name} ---")
        
        ExpertAgentClass = self._load_agent_class(expert_class_name)
        StudentAgentClass = self._load_agent_class(student_class_name)
        
        if not ExpertAgentClass or not StudentAgentClass: return

        expert = ExpertAgentClass()
        student = StudentAgentClass()

        expert_score = 0
        student_score = 0
        
        for i, task in enumerate(curriculum):
            self.logger.info(f"\nRunning Task {i+1}/{len(curriculum)}...")
            expert_result, student_result = None, None

            if "paper" in task: # Analysis Task
                self.logger.info(f"Task type: Analysis on '{task['paper']['title'][:40]}...'")
                expert_result = expert.analyze_paper(task['paper'])
                student_result = student.analyze_paper(task['paper'])
            elif "objective" in task: # Planning Task
                self.logger.info(f"Task type: Planning for '{task['objective'][:40]}...'")
                expert_result = expert.create_plan(task['objective'])
                student_result = student.create_plan(task['objective'])

            # Simple success metric: Did the agent produce a result without an "error" key?
            expert_pass = expert_result and "error" not in expert_result
            student_pass = student_result and "error" not in student_result
            
            if expert_pass: expert_score += 1
            if student_pass: student_score += 1

            self.logger.info(f"Task {i+1} Result -> Expert: {'Pass' if expert_pass else 'Fail'}, Student: {'Pass' if student_pass else 'Fail'}")

        self.logger.info("\n--- Gauntlet Results ---")
        self.logger.info(f"Expert Agent Score: {expert_score}/{len(curriculum)}")
        self.logger.info(f"Student Agent Score: {student_score}/{len(curriculum)}")

        if student_score > expert_score:
            self.logger.info("Outcome: Student has graduated and is superior. ??")
        elif student_score == expert_score:
             self.logger.info("Outcome: Student has graduated and performs equally. ??")
        else:
            self.logger.info("Outcome: Student requires more training.")
