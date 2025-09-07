# agents/discovery_agent.py
import json
import ollama

class DiscoveryAgent:
    def __init__(self):
        self.model_name = 'llama3'
        # Point the client to the Ollama service within the Docker network
        self.client = ollama.Client(host='http://ollama:11434')
        print(f"DiscoveryAgent (Containerized) Initialized for model: {self.model_name}.")

    def decide_next_action(self, user_message: str) -> dict:
        """Uses a local LLM via Ollama container to determine intent."""
        system_prompt = "..." # (Full prompt from before)
        try:
            print(f"Sending prompt to Ollama container: {self.model_name}")
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_message}
                ],
                format='json'
            )
            decision_str = response['message']['content']
            decision = json.loads(decision_str)
            print(f"Received decision from Ollama: {decision}")
            return decision
        except Exception as e:
            print(f"Error communicating with Ollama container: {e}")
            return {"action": "error", "details": str(e)}
