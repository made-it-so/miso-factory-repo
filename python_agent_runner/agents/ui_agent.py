# agents/ui_agent.py

class UIAgent:
    """
    Manages the user-facing dialogue to collaboratively engineer a prompt.
    """
    def __init__(self, conversation_state: dict):
        self.state = conversation_state

    def process_message(self, last_message: str = None):
        """
        Processes the latest user message and determines the next step in the conversation.
        """
        if last_message:
            last_message = last_message.lower()
            if self.state.get('next_action') == 'get_objective':
                self.state['objective'] = last_message
            elif self.state.get('next_action') == 'get_output_format':
                self.state['output_format'] = last_message
            elif self.state.get('next_action') == 'get_data_source':
                self.state['data_source'] = last_message

        # Determine next step in the conversation
        if 'objective' not in self.state:
            self.state['next_action'] = 'get_objective'
            response = {
                'response_type': 'text',
                'response_text': "Welcome to MISO. Please state your initial objective.",
                'clarity_score': 10
            }
        elif 'output_format' not in self.state:
            self.state['next_action'] = 'get_output_format'
            response = {
                'response_type': 'suggestions',
                'response_text': "Understood. What format should the final output be?",
                'options': ['CSV File', 'PDF Report', 'JSON Object', 'Plain Text'],
                'clarity_score': 40
            }
        elif 'data_source' not in self.state:
            self.state['next_action'] = 'get_data_source'
            response = {
                'response_type': 'file_upload',
                'response_text': "Got it. What is the data source for this task? (e.g., a filename, or you can upload it here)",
                'clarity_score': 70
            }
        else:
            # Conversation is complete, generate the final prompt
            self.state['next_action'] = 'complete'
            engineered_prompt = (
                f"OBJECTIVE: {self.state.get('objective', 'N/A')}\n"
                f"OUTPUT FORMAT: {self.state.get('output_format', 'N/A')}\n"
                f"DATA SOURCE: {self.state.get('data_source', 'N/A')}"
            )
            response = {
                'response_type': 'final_prompt',
                'response_text': "Perfect. I have everything I need. Please review the final engineered prompt.",
                'engineered_prompt': engineered_prompt,
                'clarity_score': 100
            }

        response['state'] = self.state
        return response