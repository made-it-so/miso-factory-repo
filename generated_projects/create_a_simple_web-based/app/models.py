
from app.config import Config
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)

class WorkInterval(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_session_id = db.Column(db.Integer, db.ForeignKey('usersession.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)

class Break(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    work_interval_id = db.Column(db.Integer, db.ForeignKey('workinterval.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
