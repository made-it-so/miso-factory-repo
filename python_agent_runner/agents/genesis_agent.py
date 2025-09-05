# agents/genesis_agent.py
import os
import re

class GenesisAgent:
    """
    The Genesis Agent is responsible for creating the initial codebase
    and directory structure based on a validated project proposal.
    """
    def __init__(self):
        print("  -> Genesis Agent initialized.")

    def _sanitize_filename(self, name):
        """Creates a safe directory/file name from a project name."""
        name = name.lower()
        name = re.sub(r'\s+', '_', name)
        name = re.sub(r'[^a-z0-9_]', '', name)
        return name[:50] # Limit length

    def create_codebase(self, proposal_data: dict):
        """
        Creates the project directory and placeholder file.
        """
        project_name = proposal_data.get('project_name', 'new_miso_project')
        objective = proposal_data.get('objective', '# No objective provided.')
        
        dir_name = self._sanitize_filename(project_name)
        
        try:
            # Create a directory for the project
            os.makedirs(dir_name, exist_ok=True)
            print(f"  -> Created directory: ./{dir_name}/")

            file_path = os.path.join(dir_name, 'main.py')

            # Create the main.py file with the objective as a docstring
            file_content = f'"""\nPROJECT: {project_name}\n\nOBJECTIVE:\n{objective}\n"""\n\n# MISO Genesis Agent: Code generation starts here.\n\ndef main():\n    print("Hello from the MISO-generated codebase!")\n\nif __name__ == "__main__":\n    main()\n'

            with open(file_path, 'w') as f:
                f.write(file_content)
            
            print(f"  -> Created file: {file_path}")
            print("  -> Genesis Agent task complete.")
            return True

        except Exception as e:
            print(f"  -> ERROR in Genesis Agent: {e}")
            return False
