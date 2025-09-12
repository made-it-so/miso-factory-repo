# python_agent_runner/agents/gauntlet_agent.py
import os
import openai

class GauntletAgent:
    """
    A specialist agent that uses a panel of external LLMs to refine and
    enhance a given prompt.
    """
    def __init__(self):
        # In a real system, you might initialize multiple clients
        # For this example, we'll use OpenAI
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def refine_prompt(self, draft_prompt, domain):
        print("GauntletAgent: Refining prompt...")
        try:
            # This is the prompt FOR the Gauntlet's external LLM
            gauntlet_prompt = f"""
            You will act in two roles:
            1. An expert Prompt Engineer.
            2. An expert Subject Matter Expert in '{domain}'.

            Analyze and improve the following DRAFT PROMPT to generate a better output.
            Your task is to rewrite the prompt to be more detailed, clear, and contextually aware, incorporating best practices from the specified Domain.
            Respond with only the rewritten, improved prompt.

            DRAFT PROMPT:
            "{draft_prompt}"
            """

            response = self.openai_client.chat.completions.create(
                model="gpt-4", # Or another powerful model
                messages=[{"role": "user", "content": gauntlet_prompt}]
            )
            refined_prompt = response.choices[0].message.content
            print("GauntletAgent: Prompt successfully refined.")
            return refined_prompt
        except Exception as e:
            print(f"GauntletAgent Error: {e}")
            # If the Gauntlet fails, just return the original draft
            return draft_prompt
