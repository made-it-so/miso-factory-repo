from agents.legacy_modernization_agent import LegacyModernizationAgent
from agents.genesis_agent import GenesisAgent
import os

def run_test():
    """
    Tests the first two steps of the Legacy Modernization Pipeline.
    """
    target_file_path = os.path.join('legacy_code', 'sample_payroll.cbl')
    
    print(f"Reading original code from: {target_file_path}")
    with open(target_file_path, 'r', encoding='utf-8') as f:
        original_code = f.read()

    # --- Phase 1: Create the Blueprint ---
    modernization_agent = LegacyModernizationAgent()
    blueprint = modernization_agent.create_blueprint(original_code, source_language="COBOL")
    
    print("\n\n========== BUSINESS LOGIC BLUEPRINT ==========")
    print(blueprint)
    
    # --- Phase 2: Create the Python Scaffold ---
    genesis_agent = GenesisAgent()
    scaffolding_challenge = f"""Based on the following Business Logic Blueprint, create a Python code scaffold. 
    The code should be a single class with methods corresponding to the main processing steps. 
    Include full type hints and docstrings, but leave the method bodies empty (using 'pass').

    Blueprint:
    {blueprint}
    """
    
    python_scaffold = genesis_agent.generate_challenger_code(scaffolding_challenge, "") # No original code needed

    print("\n\n========== GENERATED PYTHON SCAFFOLD ==========")
    print(python_scaffold)
    print("\n=============================================")

if __name__ == "__main__":
    run_test()
