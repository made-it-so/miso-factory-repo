import sys
import requests
import json
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/execute', methods=['POST'])
def execute_task():
    data = request.get_json()
    if not data or 'task' not in data:
        return jsonify({"error": "Invalid request"}), 400

    task_type = data.get('task')

    if task_type == 'get_info':
        result_data = {
            "status": "success",
            "agent_type": "python",
            "message": "Simple agent is online."
        }
        # Store the successful result in memory
        try:
            memory_res = requests.post("http://miso-memory:5003/store", data=json.dumps(result_data), timeout=5)
            result_data["memory_checksum"] = memory_res.json().get("checksum")
        except requests.exceptions.RequestException as e:
            result_data["memory_error"] = str(e)

        return jsonify(result_data), 200

    return jsonify({"error": f"Unknown task: {task_type}"}), 404
