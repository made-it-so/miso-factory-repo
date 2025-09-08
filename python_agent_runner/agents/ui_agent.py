# python_agent_runner/agents/ui_agent.py
from .genesis_agent import GenesisAgent

class UIAgent:
    def __init__(self):
        self.creation_sessions = {}
        self.genesis_agent = GenesisAgent()

    def process_request(self, user_input):
        session_id = 'default_user'
        if session_id in self.creation_sessions:
            session = self.creation_sessions[session_id]
            current_state = session['state']

            if current_state == 'awaiting_goal':
                session['brief']['goal'] = user_input
                session['state'] = 'awaiting_content'
                return {'response': 'Perfect. Now, what key sections or information should we include on the page?'}
            
            elif current_state == 'awaiting_content':
                session['brief']['content'] = user_input
                session['state'] = 'awaiting_vibe'
                return {'response': 'Great, we have the sections mapped out. Now, what kind of vibe are you going for?'}

            elif current_state == 'awaiting_vibe':
                session['brief']['vibe'] = user_input
                session['state'] = 'awaiting_action'
                return {'response': 'Excellent choice. Finally, what is the single most important action you want a visitor to take?'}
            
            elif current_state == 'awaiting_action':
                session['brief']['action'] = user_input
                final_brief = session['brief']
                
                creation_result = self.genesis_agent.create_website(final_brief)
                
                if creation_result['status'] == 'Success':
                    response_text = 'Fantastic! The project brief is complete. I have generated a preview of your website in the Visualizer panel.'
                    preview_url = creation_result['preview_url']
                else:
                    response_text = f'There was an error during creation: {creation_result["status"]}'
                    preview_url = None
                
                del self.creation_sessions[session_id]
                return {'response': response_text, 'preview_url': preview_url}

        elif 'make a website' in user_input.lower():
            self.creation_sessions[session_id] = { 'state': 'awaiting_goal', 'brief': {} }
            return {'response': 'I can help with that! To start, what is the primary goal of the site?'}
        
        return {'response': 'I am ready to assist. You can ask me to "make a website" to begin the creation process.'}

