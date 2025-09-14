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
        self.logger.info("GenesisAgent initialized with all sub-agents.")

    def _create_project_files(self, project_path: str, file_structure: dict) -> bool:
        """Recursively creates project files, building and passing context."""
        project_context = {}
        def process_level(current_path, structure):
            os.makedirs(current_path, exist_ok=True)
            for name, content in structure.items():
                full_path = os.path.join(current_path, name)
                relative_path = os.path.relpath(full_path, start=project_path)
                if isinstance(content, dict):
                    if not process_level(full_path, content): return False
                elif isinstance(content, str):
                    generated_code = self.code_generation_agent.generate_code(relative_path, content, project_context)
                    if generated_code is None:
                        self.logger.error(f"Halting: CodeGenerationAgent failed for {full_path}")
                        return False
                    with open(full_path, 'w', encoding='utf-8') as f: f.write(generated_code)
                    self.logger.info(f"Successfully wrote file: {full_path}")
                    if relative_path.endswith('.py'):
                        summary = summarize_python_code(generated_code)
                        project_context[relative_path] = summary
                        self.logger.info(f"Updated project context for {relative_path}")
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
        if "error" in plan: return {"status": "FAIL", "reason": "Planning phase failed.", "details": plan.get('details')}

        # 2. SIMULATE
        self.logger.info("Phase 2: Simulation...")
        sim_report = self.simulation_agent.run_simulation(plan)
        if sim_report.get("status", "FAIL").upper() == "FAIL":
            self.logger.error("Simulation failed. Halting execution.")
            return {"status": "FAIL", "reason": "Simulation failed.", "report": sim_report}
        elif sim_report.get("status").upper() == "WARNING":
            self.logger.warning("Simulation returned warnings. Proceeding with caution...")
        
        # 3. GENERATE
        self.logger.info("Phase 3: Code Generation...")
        if not self._create_project_files(project_path, plan.get("file_structure", {})):
            return {"status": "FAIL", "reason": "Code generation failed."}

        # 4. DEBUG
        self.logger.info("Phase 4: Debugging...")
        if not self.debugging_agent.debug_codebase(project_path):
            self.logger.warning("Debugging phase completed with unresolved issues.")
            # Continue to security scan even if debugging fails to provide a complete report
        
        # 5. SECURE
        self.logger.info("Phase 5: Security Scan...")
        sec_report = self.security_agent.scan_codebase(project_path)
        if sec_report.get("status") == "INSECURE":
            self.logger.warning("Security scan found potential vulnerabilities.")
            return {"status": "SUCCESS_WITH_SECURITY_WARNINGS", "reason": "Codebase generated, but security issues were found.", "output_path": project_path, "security_report": sec_report}
        elif sec_report.get("status") == "FAIL":
            self.logger.error("Security scan failed to run.")
            return {"status": "FAIL", "reason": "The security scan itself failed.", "output_path": project_path, "security_report": sec_report}

        self.logger.info(f"--- Project Pipeline Completed Successfully. Output at: {project_path} ---")
        return {"status": "SUCCESS", "reason": "Codebase generated, debugged, and secured successfully.", "output_path": project_path}
