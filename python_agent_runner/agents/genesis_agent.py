import logging
import os
import json
from .planning_agent import PlanningAgent
from .simulation_agent import SimulationAgent
from .code_generation_agent import CodeGenerationAgent
from .debugging_agent import DebuggingAgent
from .security_agent import SecurityAgent
from ..shared.code_utils import summarize_python_code

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class GenesisAgent:
    """Orchestrates the Plan -> Simulate -> Generate -> Debug -> Secure pipeline."""
    def __init__(self, output_dir="generated_projects"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.planning_agent = PlanningAgent()
        self.simulation_agent = SimulationAgent()
        self.code_generation_agent = CodeGenerationAgent()
        self.debugging_agent = DebuggingAgent()
        self.security_agent = SecurityAgent()
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _create_project_files(self, project_path: str, file_structure: dict) -> bool:
        # (Implementation is unchanged)
        project_context = {}
        try:
            def process_level(current_path, structure):
                os.makedirs(current_path, exist_ok=True)
                for name, content in structure.items():
                    full_path = os.path.join(current_path, name)
                    if isinstance(content, dict):
                        if not process_level(full_path, content): return False
                    elif isinstance(content, str):
                        os.makedirs(os.path.dirname(full_path), exist_ok=True)
                        generated_code = self.code_generation_agent.generate_code(os.path.relpath(full_path, start=project_path), content, project_context)
                        if generated_code is None: return False
                        with open(full_path, 'w', encoding='utf-8') as f: f.write(generated_code)
                        self.logger.info(f"Successfully wrote file: {full_path}")
                        if full_path.endswith('.py'):
                            summary = summarize_python_code(generated_code)
                            project_context[os.path.relpath(full_path, start=project_path)] = summary
                return True
            return process_level(project_path, file_structure)
        except Exception as e:
            self.logger.error(f"An error occurred during file creation: {e}")
            return False

    def create_codebase(self, proposal: dict):
        project_name = proposal.get('project_name', 'untitled_project').replace(' ', '_').lower()
        objective = proposal.get("objective", "No objective provided.")
        project_path = os.path.join(self.output_dir, project_name)

        self.logger.info(f"--- Starting New Project: {project_name} ---")
        
        # 1. PLAN
        self.logger.info("Phase 1: Planning...")
        plan = self.planning_agent.create_plan(objective)
        if "error" in plan: return {"status": "FAIL", "reason": "Planning phase failed.", "details": plan.get('details')}

        # 2. SIMULATE
        self.logger.info("Phase 2: Simulation...")
        sim_report = self.simulation_agent.run_simulation(plan)
        if sim_report.get("status", "FAIL").upper() == "FAIL":
            return {"status": "FAIL", "reason": "Simulation failed.", "report": sim_report}
        
        # 3. GENERATE
        self.logger.info("Phase 3: Code Generation...")
        file_structure = plan.get("file_structure")
        
        # THE FIX: Validate that the file structure exists and is not empty.
        if not file_structure or not isinstance(file_structure, dict) or not file_structure:
            self.logger.error("Planning Agent produced an empty or invalid plan. Halting.")
            return {"status": "FAIL", "reason": "Planning Agent produced an empty or invalid plan."}

        if not self._create_project_files(project_path, file_structure):
            return {"status": "FAIL", "reason": "Code generation failed."}

        # 4. DEBUG & 5. SECURE
        self.logger.info("Phase 4: Debugging...")
        self.debugging_agent.debug_codebase(project_path)
        
        self.logger.info("Phase 5: Security Scan...")
        sec_report = self.security_agent.scan_codebase(project_path)
        if sec_report.get("status") == "INSECURE":
            return {"status": "SUCCESS_WITH_SECURITY_WARNINGS", "reason": "Codebase generated, but security issues were found.", "output_path": project_path, "security_report": sec_report}

        self.logger.info(f"--- Project Pipeline Completed Successfully. Output at: {project_path} ---")
        return {"status": "SUCCESS", "reason": "Codebase generated and debugged successfully.", "output_path": project_path}
