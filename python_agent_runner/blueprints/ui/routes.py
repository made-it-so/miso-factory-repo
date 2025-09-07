# agents/ui/routes.py
from flask import Blueprint, render_template, request, jsonify
import time
from agents.ui_agent import UIAgent

ui_agent = UIAgent()
ui_bp = Blueprint('ui', __name__, template_folder='templates', static_folder='static', static_url_path='/ui/static')

@ui_bp.route('/')
def index():
    """Serves the main application page with a cache-busting version number."""
    return render_template('workspace.html', version=time.time())

@ui_bp.route('/chat', methods=['POST'])
def chat():
    """Handles incoming chat messages and returns an agent's response."""
    data = request.get_json()
    user_message = data.get('message')
    if not user_message:
        return jsonify({'error': 'Invalid request. Message not found.'}), 400
    
    agent_response_dict = ui_agent.handle_request(user_message)
    return jsonify(agent_response_dict)
