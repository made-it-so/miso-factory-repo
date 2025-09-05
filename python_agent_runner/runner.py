import subprocess
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/execute', methods=['POST'])
def execute():
    """Execute a system command and return the output. 

Args: 
    None

Returns: 
    If the command executes successfully, a JSON object with 'output' key containing the command's stdout. 
    Otherwise, a JSON object with 'error' key containing the command's stderr."""
    data = request.json
    command = data.get('command')
    input_data = data.get('input', '')
    try:
        result = subprocess.run(command, input=input_data, text=True, capture_output=True, shell=True, check=True)
        return jsonify({'output': result.stdout.strip()})
    except subprocess.CalledProcessError as e:
        return (jsonify({'error': e.stderr.strip()}), 500)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)