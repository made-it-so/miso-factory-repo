import logging
import ollama
from .planning_agent import PlanningAgent
from .simulation_agent import SimulationAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class GenesisAgent:
    """
    Orchestrates the Plan -> Simulate -> Generate pipeline.
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.planning_agent = PlanningAgent()
        self.simulation_agent = SimulationAgent()
        self.logger.info("GenesisAgent initialized with Planning and Simulation sub-agents.")

    def create_codebase(self, proposal: dict):
        """
        The main entry point to create a new codebase from a proposal.
        """
        objective = proposal.get("objective", "No objective provided.")
        project_name = proposal.get('project_name', 'Untitled')
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
        if status in ["FAIL", "WARNING"]:
            self.logger.error("Simulation failed or returned warnings. Halting execution.")
            self.logger.error(f"Report: {simulation_report}")
            return {"status": "FAIL", "reason": "Simulation phase failed or has warnings.", "report": simulation_report}

        # 3. GENERATE (Placeholder for now)
        self.logger.info("Phase 3: Code Generation...")
        # The actual code generation logic would be implemented here,
        # using the detailed 'plan' to guide one or more CodeGenerationAgents.
        self.logger.info("Code generation would proceed here based on the validated plan.")
        
        self.logger.info("--- Project Pipeline Completed Successfully ---")
        return {"status": "SUCCESS", "reason": "Plan created and validated successfully.", "plan": plan}
