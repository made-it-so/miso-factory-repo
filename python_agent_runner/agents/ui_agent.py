# python_agent_runner/agents/ui_agent.py
import ollama
import json
from .genesis_agent import GenesisAgent
from .ontology_agent import OntologyAgent

class UIAgent:
    def __init__(self):
        self.creation_sessions = {}
        self.genesis_agent = GenesisAgent()
        self.ontology_agent = OntologyAgent()

    def process_request(self, user_input, user_id):
        # (Your existing analyze/explain logic can remain here)

        if user_id not in self.creation_sessions:
            self.creation_sessions[user_id] = {
                'history': [{'role': 'system', 'content': 'You are an expert project manager...'}],
                'brief': {}
            }
        
        session = self.creation_sessions[user_id]
        session['history'].append({'role': 'user', 'content': user_input})

        try:
            # GAM-Inspired Prompting: Combine global brief with local history
            prompt = f"""
            You are an expert project manager. Your task is to have a dialogue with a user to define a project.

            GLOBAL CONTEXT (The current project brief):
            {json.dumps(session.get('brief', {}), indent=2)}

            RECENT CONVERSATION (The last 4 turns):
            {session['history'][-4:]}

            YOUR TASK:
            Analyze the user's last message in the context of the brief and recent conversation.
            1. Update the project brief.
            2. Decide if the brief is complete.
            3. Formulate the next response to the user.
            Respond with a single, valid JSON object containing three keys: "response_type" (either "dialogue" or "handoff"), "brief" (the updated JSON brief), and "response" (your next message to the user).
            """
            
            response = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': prompt}])
            llm_output_text = response['message']['content'].strip()
            
            if "```json" in llm_output_text:
                llm_output_text = llm_output_text.split("```json", 1)[1].split("```")[0]
            
            llm_data = json.loads(llm_output_text)

            session['brief'] = llm_data.get('brief', session['brief'])
            miso_response = llm_data.get('response', "I'm sorry, I encountered an issue.")
            
            if llm_data.get('response_type') == 'handoff':
                creation_result = self.genesis_agent.create_website(session['brief'])
                del self.creation_sessions[user_id]
                return {'response': f"{miso_response}\n\nProject brief complete! Building prototype...", 'preview_url': creation_result.get('preview_url')}
            else:
                session['history'].append({'role': 'assistant', 'content': miso_response})
                return {'response': miso_response}

        except Exception as e:
            return {'response': f"Error communicating with the Cognitive Core: {str(e)}"}
