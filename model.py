from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Chatroom(db.Model):
    room_id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(24), nullable=False)

    messages = db.relationship('Message', backref='room', lazy='dynamic')

    def __init__(self, room_name):
        self.room_name = room_name

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24), nullable=False)
    password = db.Column(db.String(20), nullable=False)

    messages = db.relationship('Message', backref='author', lazy='dynamic')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Message(db.Model):
    message_id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    room_id = db.Column(db.Integer, db.ForeignKey('chatroom.room_id'))
    text = db.Column(db.Text, nullable=False)

    def __init__(self, author, room, text):
        self.author = author
        self.room = room
        self.text = text
