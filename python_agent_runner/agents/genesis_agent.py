import logging
import ollama
import os
import json
from .planning_agent import PlanningAgent
from .simulation_agent import SimulationAgent
from .code_generation_agent import CodeGenerationAgent
from .debugging_agent import DebuggingAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class GenesisAgent:
    """Orchestrates the Plan -> Simulate -> Generate -> Debug pipeline."""
    def __init__(self, output_dir="generated_projects"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.planning_agent = PlanningAgent()
        self.simulation_agent = SimulationAgent()
        self.code_generation_agent = CodeGenerationAgent()
        self.debugging_agent = DebuggingAgent()
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.logger.info("GenesisAgent initialized with all sub-agents.")

    def _create_project_files(self, project_path: str, file_structure: dict) -> bool:
        """Recursively creates the project files and directories."""
        def process_level(current_path, structure):
            os.makedirs(current_path, exist_ok=True)
            for name, content in structure.items():
                full_path = os.path.join(current_path, name)
                if isinstance(content, dict):
                    if not process_level(full_path, content): return False
                elif isinstance(content, str):
                    generated_code = self.code_generation_agent.generate_code(full_path, content)
                    if generated_code is None:
                        self.logger.error(f"Halting due to failure in generating {full_path}")
                        return False
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(generated_code)
                    self.logger.info(f"Successfully wrote file: {full_path}")
            return True
        return process_level(project_path, file_structure)

    def create_codebase(self, proposal: dict):
        """The main entry point to create a new codebase from a proposal."""
        project_name = proposal.get('project_name', 'untitled_project').replace(' ', '_').lower()
        objective = proposal.get("objective", "No objective provided.")
        self.logger.info(f"--- Starting New Project: {project_name} ---")
        project_path = os.path.join(self.output_dir, project_name)

        # 1. PLAN
        self.logger.info("Phase 1: Planning...")
        plan = self.planning_agent.create_plan(objective)
        if "error" in plan:
            return {"status": "FAIL", "reason": "Planning phase failed.", "details": plan.get('details')}

        # 2. SIMULATE
        self.logger.info("Phase 2: Simulation...")
        simulation_report = self.simulation_agent.run_simulation(plan)
        if simulation_report.get("status", "FAIL").upper() != "PASS":
            self.logger.error(f"Simulation did not pass. Halting execution.")
            return {"status": "FAIL", "reason": f"Simulation status was {simulation_report.get('status')}.", "report": simulation_report}

        # 3. GENERATE
        self.logger.info("Phase 3: Code Generation...")
        file_structure = plan.get("file_structure")
        if not file_structure:
            return {"status": "FAIL", "reason": "Plan is invalid, missing 'file_structure'."}
        if not self._create_project_files(project_path, file_structure):
            return {"status": "FAIL", "reason": "Code generation failed for one or more files."}

        # 4. DEBUG
        self.logger.info("Phase 4: Debugging...")
        if not self.debugging_agent.debug_codebase(project_path):
            self.logger.warning("Debugging phase completed with unresolved issues.")
            return {"status": "SUCCESS_WITH_WARNINGS", "reason": "Codebase generated, but debugging could not fix all issues.", "output_path": project_path}
        
        self.logger.info(f"--- Project Pipeline Completed Successfully. Output at: {project_path} ---")
        return {"status": "SUCCESS", "reason": "Codebase generated and debugged successfully.", "output_path": project_path}
