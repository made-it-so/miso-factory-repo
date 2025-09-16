
from flask import Flask
from app.config import Config
from app.routes.user import user_routes
from app.routes.auth import auth_routes

app = Flask(__name__)
app.config.from_object(Config())

@app.route('/')
def index():
    return 'Welcome to the App!'

app.register_blueprint(user_routes)
app.register_blueprint(auth_routes)

if __name__ == '__main__':
    app.run(debug=False)
