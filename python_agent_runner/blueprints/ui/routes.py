# python_agent_runner/blueprints/ui/routes.py
from flask import Blueprint, render_template, request, jsonify
from agents.ui_agent import UIAgent
import sqlite3
import os

# Corrected: Renamed 'ui_blueprint' to 'ui_bp' to match the import in app.py
ui_bp = Blueprint('ui', __name__, template_folder='templates', static_folder='static')
ui_agent = UIAgent()

# --- Database Setup for Feedback ---
DB_PATH = 'feedback.db'

def init_feedback_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT NOT NULL,
                feedback TEXT NOT NULL,
                context TEXT
            )
        """)
        conn.commit()
        conn.close()

init_feedback_db()
# --- End of Database Setup ---

@ui_bp.route('/')
def workspace():
    return render_template('workspace.html')

@ui_bp.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    message = data.get('message')
    user_id = data.get('user_id', 'anonymous')
    response_data = ui_agent.process_request(message, user_id)
    return jsonify(response_data)

@ui_bp.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    # ... (feedback logic remains here) ...
    return jsonify({'status': 'success'}), 200
