import redis
import hashlib
import json
from flask import Flask, jsonify, request, Response

app = Flask(__name__)
# The service name 'miso-redis' will be resolved by Docker's internal DNS.
db = redis.Redis(host='miso-redis', port=6379, db=0, decode_responses=False)

@app.route('/store', methods=['POST'])
def store_memory():
    data = request.get_data()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    checksum = hashlib.sha256(data).hexdigest()
    db.set(checksum, data)

    return jsonify({"status": "success", "checksum": checksum}), 200

@app.route('/retrieve/<checksum>', methods=['GET'])
def retrieve_memory(checksum):
    data = db.get(checksum)
    if data is None:
        return jsonify({"error": "Checksum not found"}), 404

    # Return raw data with appropriate content type if it's JSON
    try:
        json.loads(data) # Just to validate if it's JSON
        return Response(data, mimetype='application/json')
    except json.JSONDecodeError:
        return Response(data, mimetype='text/plain')
