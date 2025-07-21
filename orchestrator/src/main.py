import os, jwt, docker, requests, datetime
from functools import wraps
from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-key')
users = { "admin": { "password_hash": generate_password_hash("password"), "role": "admin" } }

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers: token = request.headers['Authorization'].split(" ")[1]
        if not token: return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            kwargs['current_user_role'] = users.get(data['user'], {}).get('role')
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['POST'])
def login():
    auth = request.json
    user = users.get(auth.get('username'))
    if user and check_password_hash(user['password_hash'], auth.get('password')):
        token = jwt.encode({'user': auth['username'], 'role': user['role'], 'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)}, app.config['SECRET_KEY'])
        return jsonify({'token': token})
    return jsonify({'message': 'Login failed!'}), 401

@app.route('/dispatch', methods=['POST'])
@token_required
def dispatch_task(current_user_role):
    task_payload = request.get_json()
    if task_payload.get('task') == 'execute_gcloud' and current_user_role != 'admin':
        return jsonify({"error": "Permission denied: 'admin' role required"}), 403
    try:
        docker_client = docker.from_env()
        agent_container = docker_client.containers.get("miso-python-agent")
        agent_ip = agent_container.attrs['NetworkSettings']['Networks']['miso-net']['IPAddress']
        agent_url = f"http://{agent_ip}:5002/execute"
        response = requests.post(agent_url, json=task_payload, timeout=30)
        response.raise_for_status()
        return response.json(), response.status_code
    except Exception as e:
        return jsonify({"error": f"Dispatch failed: {str(e)}"}), 500
