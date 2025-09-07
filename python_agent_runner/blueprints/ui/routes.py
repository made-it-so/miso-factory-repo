# agents/ui/routes.py
from flask import Blueprint, render_template, request, jsonify
import time, json
from agents.ui_agent import UIAgent

ui_agent = UIAgent()
ui_bp = Blueprint('ui', __name__, template_folder='templates', static_folder='static', static_url_path='/ui/static')

@ui_bp.route('/')
def index():
    return render_template('workspace.html', version=time.time())

@ui_bp.route('/chat', methods=['POST'])
def chat():
    """Main endpoint for all chat messages."""
    response_data = ui_agent.handle_request(request.get_json().get('message'))
    return jsonify(response_data)

# --- NEW: Endpoint to receive decisions from the modal ---
@ui_bp.route('/api/decision', methods=['POST'])
def handle_decision():
    data = request.get_json()
    print(f"Received user decision: {data}")
    # In the future, this is where we would log the winner to improve the agents.
    with open('decision_log.log', 'a') as f:
        f.write(json.dumps(data) + '\n')
    return jsonify({'status': 'success'})

# The old /arena and /gauntlet routes are no longer needed
