from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from agents.catalyst_agent import CatalystAgent

ui_bp = Blueprint('ui', __name__, template_folder='templates', static_folder='static', static_url_path='/ui/static')

@ui_bp.route('/')
def index():
    return render_template('proposal.html')

@ui_bp.route('/submit_proposal', methods=['POST'])
def submit_proposal():
    objective = request.form.get('objective')
    proposal_data = {
        'project_name': 'Engineered Proposal',
        'description': 'Generated via conversational UI',
        'objective': objective
    }
    catalyst = CatalystAgent()
    catalyst.initiate_proposal(proposal_data)
    flash('Success! Your proposal has been sent to the MISO Orchestrator.', 'success')
    return redirect(url_for('ui.index'))

@ui_bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    conversation_state = data.get('state', {})
    
    if 'last_message' in data:
        last_message = data['last_message'].lower()
        if conversation_state.get('next_action') == 'get_objective':
            conversation_state['objective'] = last_message
        elif conversation_state.get('next_action') == 'get_output_format':
            conversation_state['output_format'] = last_message
        elif conversation_state.get('next_action') == 'get_data_source':
            conversation_state['data_source'] = last_message

    if 'objective' not in conversation_state:
        conversation_state['next_action'] = 'get_objective'
        response = {
            'response_type': 'text',
            'response_text': "Welcome to MISO. Please state your initial objective.",
            'clarity_score': 10
        }
    elif 'output_format' not in conversation_state:
        conversation_state['next_action'] = 'get_output_format'
        response = {
            'response_type': 'suggestions',
            'response_text': "Understood. What format should the final output be?",
            'options': ['CSV File', 'PDF Report', 'JSON Object', 'Plain Text'],
            'clarity_score': 40
        }
    elif 'data_source' not in conversation_state:
        conversation_state['next_action'] = 'get_data_source'
        response = {
            'response_type': 'file_upload',
            'response_text': "Got it. What is the data source for this task? (e.g., a filename, or you can upload it here)",
            'clarity_score': 70
        }
    else:
        conversation_state['next_action'] = 'complete'
        engineered_prompt = (
            f"OBJECTIVE: {conversation_state.get('objective', 'N/A')}\n"
            f"OUTPUT FORMAT: {conversation_state.get('output_format', 'N/A')}\n"
            f"DATA SOURCE: {conversation_state.get('data_source', 'N/A')}"
        )
        response = {
            'response_type': 'final_prompt',
            'response_text': "Perfect. I have everything I need. Please review the final engineered prompt.",
            'engineered_prompt': engineered_prompt,
            'clarity_score': 100
        }

    response['state'] = conversation_state
    return jsonify(response)
