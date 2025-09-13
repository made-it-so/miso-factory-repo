import logging
import ollama
import os
import json
from .planning_agent import PlanningAgent
from .simulation_agent import SimulationAgent
from .code_generation_agent import CodeGenerationAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class GenesisAgent:
    """Orchestrates the Plan -> Simulate -> Generate pipeline."""
    def __init__(self, output_dir="generated_projects"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.planning_agent = PlanningAgent()
        self.simulation_agent = SimulationAgent()
        self.code_generation_agent = CodeGenerationAgent()
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.logger.info("GenesisAgent initialized with all sub-agents.")

    def _create_project_files(self, project_name: str, file_structure: dict) -> bool:
        """Recursively creates the project files and directories."""
        project_root = os.path.join(self.output_dir, project_name)
        
        # Helper function to recursively process the file structure
        def process_level(current_path, structure):
            os.makedirs(current_path, exist_ok=True)
            for name, content in structure.items():
                full_path = os.path.join(current_path, name)
                if isinstance(content, dict): # It's a directory
                    if not process_level(full_path, content):
                        return False
                elif isinstance(content, str): # It's a file
                    generated_code = self.code_generation_agent.generate_code(full_path, content)
                    if generated_code is None:
                        self.logger.error(f"Halting due to failure in generating {full_path}")
                        return False # Halt-on-error
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(generated_code)
                    self.logger.info(f"Successfully wrote file: {full_path}")
            return True

        return process_level(project_root, file_structure)

    def create_codebase(self, proposal: dict):
        """The main entry point to create a new codebase from a proposal."""
        objective = proposal.get("objective", "No objective provided.")
        project_name = proposal.get('project_name', 'untitled_project').replace(' ', '_').lower()
        self.logger.info(f"--- Starting New Project: {project_name} ---")

        # 1. PLAN
        self.logger.info("Phase 1: Planning...")
        plan = self.planning_agent.create_plan(objective)
        if "error" in plan:
            self.logger.error(f"Planning failed: {plan.get('details')}")
            return {"status": "FAIL", "reason": "Planning phase failed.", "details": plan.get('details')}

        # 2. SIMULATE
        self.logger.info("Phase 2: Simulation...")
        simulation_report = self.simulation_agent.run_simulation(plan)
        status = simulation_report.get("status", "FAIL").upper()
        
        self.logger.info(f"Simulation complete. Status: {status}")
        if status != "PASS":
            self.logger.error(f"Simulation did not pass ({status}). Halting execution.")
            return {"status": "FAIL", "reason": f"Simulation status was {status}.", "report": simulation_report}

        # 3. GENERATE
        self.logger.info("Phase 3: Code Generation...")
        file_structure = plan.get("file_structure")
        if not file_structure:
            self.logger.error("Plan is missing 'file_structure'. Cannot generate code.")
            return {"status": "FAIL", "reason": "Plan is invalid."}

        success = self._create_project_files(project_name, file_structure)
        if not success:
            return {"status": "FAIL", "reason": "Code generation failed for one or more files."}
        
        self.logger.info(f"--- Project Pipeline Completed Successfully. Output at: {os.path.join(self.output_dir, project_name)} ---")
        return {"status": "SUCCESS", "reason": "Codebase generated successfully.", "output_path": os.path.join(self.output_dir, project_name)}
