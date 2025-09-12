# python_agent_runner/agents/test_subject.py
from flask import Flask, jsonify

class DataService:
    def __init__(self, data):
        self.data = data

    def get_all_items(self):
        return self.data

def create_app():
    app = Flask(__name__)
    service = DataService({"items": ["apple", "banana", "cherry"]})

    @app.route('/items')
    def get_items():
        items = service.get_all_items()
        return jsonify(items)

    return app
