from flask import Flask, jsonify

# Initialize the Flask application
app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify service status.
    """
    response = {
        'status': 'ok',
        'service': 'MISO Orchestrator',
        'version': '0.1'
    }
    return jsonify(response), 200

if __name__ == '__main__':
    # This block is for local development testing only.
    # In production, a WSGI server like Gunicorn will run the app.
    app.run(host='0.0.0.0', port=5001)
