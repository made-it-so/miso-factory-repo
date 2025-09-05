from flask import Flask, jsonify, request, send_from_directory
import os
import threading
from werkzeug.utils import secure_filename

# MISO Agent Imports
from agents.cognitive_engine import CognitiveReasoningEngine
from agents.catalyst_agent import CatalystAgent
from agents.vision_agent import VisionAgent
from agents.discovery_agent import DiscoveryAgent
from run_genesis_test import run_colosseum_challenge

# --- MISO Core Initialization ---
print("Initializing MISO Agents...")
cognitive_engine = CognitiveReasoningEngine()
catalyst_agent = CatalystAgent()
vision_agent = VisionAgent()
discovery_agent = DiscoveryAgent()
print("All MISO agents initialized.")
# ---

# Setup Upload Folder
UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- API Endpoints ---
@app.route('/api/query', methods=['POST'])
def handle_query():
    if not request.json or 'question' not in request.json:
        return jsonify({'error': 'Invalid request'}), 400
    question = request.json['question']
    try:
        result = catalyst_agent.process_request(question)
        return jsonify(result)
    except Exception as e:
        print(f"Error during agent processing: {e}")
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/api/colosseum/challenge', methods=['POST'])
def handle_colosseum_challenge():
    data = request.get_json()
    if not data or 'challenge' not in data or 'target_file' not in data:
        return jsonify({'error': 'Request must include challenge and target_file'}), 400
    challenge = data['challenge']
    target_file = data['target_file']
    thread = threading.Thread(target=run_colosseum_challenge, args=(challenge, target_file))
    thread.start()
    return jsonify({'status': 'Colosseum challenge initiated. See server console for progress.'})

@app.route('/api/vision/generate', methods=['POST'])
def handle_vision_to_code():
    if 'image' not in request.files or 'prompt' not in request.form:
        return jsonify({'error': 'Request must include image and prompt'}), 400
    image_file = request.files['image']
    prompt = request.form['prompt']
    filename = secure_filename(image_file.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image_file.save(image_path)
    def vision_to_code_task():
        blueprint = vision_agent.create_blueprint_from_image(prompt, image_path)
        target_filename = f"generated_{filename}.html"
        target_filepath = os.path.join('agents', target_filename)
        with open(target_filepath, 'w') as f: f.write("")
        run_colosseum_challenge(challenge=blueprint, target_file=target_filename)
        os.remove(image_path)
        os.remove(target_filepath)
    thread = threading.Thread(target=vision_to_code_task)
    thread.start()
    return jsonify({'status': 'Vision-to-Code process initiated. See server console for progress.'})

@app.route('/api/discovery/start', methods=['POST'])
def handle_discovery_start():
    data = request.get_json()
    if not data or 'idea_description' not in data:
        return jsonify({'error': 'Request must include an idea_description'}), 400
    idea = data['idea_description']
    result = discovery_agent.start_interview(idea)
    return jsonify(result)

# --- Frontend & Health Check ---
#@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route("/health")
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    import waitress
    waitress.serve(app, host='0.0.0.0', port=5000)

# --- Blueprint Registration ---
# Import and register the UI blueprint
from blueprints.ui.routes import ui_bp
app.register_blueprint(ui_bp, url_prefix='/')


# --- Secret Key Configuration ---
# Required for session management and flashing messages
import os
app.config['SECRET_KEY'] = os.urandom(24)

