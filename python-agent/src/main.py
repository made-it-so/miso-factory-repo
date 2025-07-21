import sys
import subprocess
from flask import Flask, jsonify, request

app = Flask(__name__)

def run_shell_command(command_array):
    try:
        result = subprocess.run(
            command_array,
            capture_output=True, text=True, check=True
        )
        return {"status": "success", "output": result.stdout}, 200
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": e.stderr}, 500
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/execute', methods=['POST'])
def execute_task():
    data = request.get_json()
    if not data or 'task' not in data:
        return jsonify({"error": "Invalid request"}), 400

    task_type = data.get('task')

    if task_type == 'get_info':
        return jsonify({
            "status": "success",
            "agent_type": "python",
            "message": "Replicator agent is online."
        }), 200

    if task_type == 'execute_gcloud':
        command_args = data.get('command_args')
        if not command_args or not isinstance(command_args, list):
            return jsonify({"error": "command_args must be a list"}), 400

        # Prepend 'gcloud' to the command for security
        return run_shell_command(['gcloud'] + command_args)

    return jsonify({"error": f"Unknown task: {task_type}"}), 404
