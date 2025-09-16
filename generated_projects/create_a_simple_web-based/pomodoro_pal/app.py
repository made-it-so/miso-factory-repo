
from flask import Flask, jsonify, request
import time

app = Flask(__name__)

@app.route('/start', methods=['POST'])
def start_pomodoro():
    if request.json:
        duration = int(request.json['duration'])
        print(f"Starting a {duration} minute pomodoro timer")
        for i in range(duration):
            print(f"{int((i+1) / (duration/60)*100)}% remaining...")
            time.sleep(60)
        return jsonify({'result': 'Pomodoro finished!'})

@app.route('/stop', methods=['POST'])
def stop_pomodoro():
    if request.json:
        print("Stopping the pomodoro timer")
        return jsonify({'result': 'Pomodoro stopped!'})

if __name__ == '__main__':
    app.run(debug=True)
