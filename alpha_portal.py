from flask import Flask, jsonify, request, render_template
from python_agent_runner.agents.genesis_agent import GenesisAgent
import uuid
import threading
import json
from collections import deque
import logging
import ollama
import chromadb

# --- NEW: Setup for RAG ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
try:
    chroma_client = chromadb.PersistentClient(path="miso_code_db")
    code_collection = chroma_client.get_collection(name="miso_source_code")
    logging.info("Successfully connected to MISO code vector database.")
except Exception as e:
    logging.warning(f"Could not connect to MISO code DB. Self-query will fail. Run create_code_index.py. Error: {e}")
    code_collection = None
# --- END NEW ---

app = Flask(__name__)
tasks = {}

class TaskLogHandler(logging.Handler):
    def __init__(self, task_id):
        super().__init__()
        self.task_id = task_id
        if 'logs' not in tasks[self.task_id]:
            tasks[self.task_id]['logs'] = deque(maxlen=100)
    def emit(self, record):
        tasks[self.task_id]['logs'].append(self.format(record))

def run_miso_pipeline(task_id, objective, project_name):
    task_handler = TaskLogHandler(task_id)
    logging.getLogger().addHandler(task_handler)
    tasks[task_id]['status'] = 'RUNNING'
    try:
        genesis_agent = GenesisAgent()
        proposal = {"project_name": project_name, "objective": objective}
        result = genesis_agent.create_codebase(proposal)
        tasks[task_id]['result'] = result
        tasks[task_id]['status'] = 'COMPLETE'
    except Exception as e:
        logging.error(f"Pipeline failed for task {task_id}: {e}")
        tasks[task_id]['status'] = 'FAILED'
        tasks[task_id]['result'] = {"error": str(e)}
    finally:
        logging.getLogger().removeHandler(task_handler)

@app.route('/')
def index():
    return render_template('portal.html')

@app.route('/api/create', methods=['POST'])
def create_task():
    if not request.is_json: return jsonify({"error": "Request must be JSON"}), 400
    objective = request.json.get('objective')
    if not objective: return jsonify({"error": "Missing 'objective'"}), 400
    task_id = str(uuid.uuid4())
    project_name = " ".join(objective.split()[:4]).replace(" ", "_")
    tasks[task_id] = {'status': 'PENDING'}
    thread = threading.Thread(target=run_miso_pipeline, args=(task_id, objective, project_name))
    thread.start()
    return jsonify({"task_id": task_id})

@app.route('/api/status/<task_id>')
def get_status(task_id):
    task = tasks.get(task_id)
    if not task: return jsonify({"error": "Task not found"}), 404
    log_output = "\n".join(task.get('logs', ['No logs yet...']))
    return jsonify({"task_id": task_id, "status": task.get('status'), "log_output": log_output, "result": task.get('result')})

@app.route('/api/query', methods=['POST'])
def handle_query():
    """API endpoint to answer questions about MISO's codebase."""
    if not request.is_json or "question" not in request.json:
        return jsonify({"error": "Request must be JSON with a 'question' field"}), 400
    if not code_collection:
        return jsonify({"answer": "Sorry, the MISO code database is not available. Please run `create_code_index.py` first."}), 503

    question = request.json["question"]
    logging.info(f"Received query: {question}")

    try:
        response = ollama.embeddings(model='mxbai-embed-large', prompt=question)
        results = code_collection.query(query_embeddings=[response["embedding"]], n_results=5)
        context_docs = "\n---\n".join(results['documents'][0])
    
        prompt = f"You are MISO, an AI Software Architect. Answer the user's question based ONLY on the following relevant snippets from your own source code. If the answer is not in the context, say so.\n\n**CONTEXT:**\n{context_docs}\n\n**QUESTION:**\n{question}\n\n**ANSWER:**"
        llm_response = ollama.chat(model="llama3", messages=[{'role': 'user', 'content': prompt}])
        answer = llm_response['message']['content']
    except Exception as e:
        logging.error(f"Error during RAG query: {e}")
        return jsonify({"answer": "An error occurred while processing your query."}), 500
    
    return jsonify({"answer": answer})

@app.route('/api/feedback', methods=['POST'])
def handle_feedback():
    """API endpoint to receive and log user feedback."""
    if not request.is_json:
        return jsonify({"message": "Error: Request must be JSON"}), 400
    
    feedback_data = request.json
    
    # Basic validation
    if 'rating' not in feedback_data or 'comments' not in feedback_data:
        return jsonify({"message": "Error: Missing 'rating' or 'comments' field"}), 400

    # Log the feedback to a file
    log_file = "feedback_log.jsonl"
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(feedback_data) + '\n')
        logging.info(f"Received feedback: {feedback_data}")
        return jsonify({"message": "Thank you, your feedback has been received!"}), 200
    except Exception as e:
        logging.error(f"Failed to write feedback to log: {e}")
        return jsonify({"message": "Error: Could not save feedback."}), 500

if __name__ == '__main__':
    app.run(debug=False, port=5000)

