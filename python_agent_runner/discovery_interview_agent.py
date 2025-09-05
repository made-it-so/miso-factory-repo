# discovery_interview_agent.py
# Owner: MISO
# Manifest Version: v31.0
# Purpose: The orchestrating agent for the Application Forge Phase 1.
# This agent manages the user conversation and delegates tasks to specialist agents.

# --- MISO Component Imports ---
# For now, we import directly. In a production mesh, this would be an API call.
from auditor_compliance import AuditorComplianceAgent, DataScientistAgentMock
from cognitive_engine import CognitiveReasoningEngine
from shared.data_contracts import ConversationContext

class DiscoveryInterviewAgent:
    """
    Orchestrates the user-facing discovery interview, tying all Phase 1 components together.
    """
    def __init__(self):
        # Instantiate dependencies
        # In a real scenario, these would be retrieved from a service locator or mesh broker.
        mock_ds_agent = DataScientistAgentMock()
        self.auditor_agent = AuditorComplianceAgent(data_scientist_agent=mock_ds_agent)
        self.cognitive_engine = CognitiveReasoningEngine()
        print("--- MISO Discovery Interview Agent Initialized ---")
        print("Specialist agents (Auditor, Cognitive Engine) are online.")

    def run_interview(self):
        """
        Starts and manages the main conversational loop with the user.
        """
        print("\nWelcome to the MISO Application Forge.")
        print("Please describe the application you want to build. Type 'quit' when you are finished.")
        
        # Initialize the stateful data contract for the conversation
        context = ConversationContext(
            full_transcript="",
            latest_user_utterance="",
            inquisitor_interventions=0 # Placeholder for now
        )

        while True:
            # 1. Get user input
            user_input = input("\n> ")
            if user_input.lower() in ['quit', 'exit']:
                print("\nThank you for using the MISO Application Forge. Exiting.")
                break
            
            # 2. Update the conversation context
            context.latest_user_utterance = user_input
            context.full_transcript += f"\nUser: {user_input}"
            # A simple heuristic for domain keywords
            context.project_domain_keywords.extend([word for word in user_input.lower().split() if word in self.cognitive_engine.metaphor_map])
            
            # 3. Delegate to specialist agents
            print("\n[MISO]...analyzing...")
            context.clarity_score = self.auditor_agent.calculate_clarity_score(context.__dict__)
            context.project_metaphor = self.cognitive_engine.generate_metaphor(context.__dict__)

            # 4. Report status to the user
            print("\n--- CURRENT PROJECT STATUS ---")
            print(f"Clarity Score: {context.clarity_score:.2f} / 1.00")
            print(f"Project Metaphor: {context.project_metaphor}")
            print("------------------------------")
            print("Please provide more details or type 'quit' to exit.")

if __name__ == '__main__':
    main_agent = DiscoveryInterviewAgent()
    main_agent.run_interview()

