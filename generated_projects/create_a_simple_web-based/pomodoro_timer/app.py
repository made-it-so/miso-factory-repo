
from flask import Flask, request, session
import time

app = Flask(__name__)
app.secret_key = 'supersecretkeythatshouldbechanged'

@app.route('/')
def index():
    return '''
        <html>
            <head>
                <title>Pomodoro Timer</title>
            </head>
            <body>
                <h1>Pomodoro Timer</h1>
                <form action="/start">
                    <input type="submit" value="Start 25-minute work session">
                </form>
            </body>
        </html>
    '''

@app.route('/start', methods=['POST'])
def start_session():
    if 'session_start' not in session:
        session['session_start'] = time.time()
        return '''
            <html>
                <head>
                    <title>Pomodoro Timer</title>
                </head>
                <body>
                    <h1>Session started!</h1>
                    <script>
                        setTimeout(() => {
                            window.location.href = '/end';
                        }, 1500 * 25); // wait for 25 minutes
                    </script>
                </body>
            </html>
        '''
    else:
        return 'You already have a session running!'

@app.route('/end', methods=['GET'])
def end_session():
    if 'session_start' in session:
        duration = time.time() - session.pop('session_start')
        return f'''
            <html>
                <head>
                    <title>Pomodoro Timer</title>
                </head>
                <body>
                    <h1>Session ended!</h1>
                    <p>You took {duration/60:.2f} minutes to complete your task.</p>
                    <script>
                        setTimeout(() => {
                            window.location.href = '/';
                        }, 5000); // wait for 5 seconds
                    </script>
                </body>
            </html>
        '''
    else:
        return 'You do not have a session running!'

if __name__ == '__main__':
    app.run(debug=True)
