import argparse
import json
import os
from python_agent_runner.agents.genesis_agent import GenesisAgent
from python_agent_runner.agents.prompt_enhancer_agent import PromptEnhancerAgent

def main():
    """Main function to run the MISO CLI."""
    parser = argparse.ArgumentParser(
        description="MISO AI Development Assistant CLI.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # 'create' command
    create_parser = subparsers.add_parser("create", help="Create a new project from an objective.")
    group = create_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-o", "--objective", type=str, help="A string containing the project objective.")
    group.add_argument("-f", "--file", type=str, help="A path to a text file containing the project objective.")

    args = parser.parse_args()

    if args.command == "create":
        raw_objective = ""
        project_name = "cli_project"

        if args.objective:
            raw_objective = args.objective
            project_name = " ".join(raw_objective.split()[:4])
        elif args.file:
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    raw_objective = f.read()
                project_name = os.path.splitext(os.path.basename(args.file))[0]
            except FileNotFoundError:
                print(f"Error: The file '{args.file}' was not found.")
                return
            except Exception as e:
                print(f"An error occurred reading the file: {e}")
                return

        if not raw_objective:
            print("Error: An objective must be provided.")
            return

        print("--- [MISO CLI] ---")
        
        # Phase 0: Prompt Enhancement
        print("Phase 0: Enhancing objective...")
        enhancer = PromptEnhancerAgent()
        enhanced_objective = enhancer.enhance_objective(raw_objective)
        print("--- Enhanced Objective ---")
        print(enhanced_objective)
        print("--------------------------")

        proposal = {
            "project_name": project_name,
            "objective": enhanced_objective
        }

        genesis_agent = GenesisAgent()
        print("\nInvoking the GenesisAgent pipeline...")
        result = genesis_agent.create_codebase(proposal)

        print("\n--- [PIPELINE COMPLETE] ---")
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
