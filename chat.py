import os
import json
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack

from model import *

app = Flask(__name__)

# configuration
DEBUG = True
SECRET_KEY = 'development key'
SQLALCHEMY_TRACK_MODIFICATIONS = True

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'chat.db')

app.config.from_object(__name__)
app.config.from_envvar('CHAT_SETTINGS', silent=True)

db.init_app(app)

@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    db.create_all()
    print('Initialized the database.')


@app.before_request
def before_request():
    g.user = None
    g.room = None
    if 'user_id' in session:
        g.user = User.query.filter_by(user_id=session['user_id']).first()
    if 'chatroom' in session:
        g.room = Chatroom.query.filter_by(room_id=session['chatroom']).first()


@app.route('/')
def chat():
    if 'user_id' in session:
        allrooms = Chatroom.query.all()
        return render_template('chat.html', rooms=allrooms)
    return render_template('layout.html')

@app.route('/<roomname>', methods=['GET', 'POST'])
def room(roomname):
    if request.method != 'POST' and not g.room and roomname != None:
        enter_room = Chatroom.query.filter_by(room_name=roomname).first()
        if enter_room == None:
            return render_template('chat.html')
        session['chatroom'] = enter_room.room_id
        before_request()
        messages = Message.query.filter_by(room_id=enter_room.room_id).all()
        for i in messages:
            session[str(i.message_id)] = str(i.message_id)
        return render_template('room.html', room=roomname, messages=messages)

    if request.method == 'POST':
        create_message = Message(g.user, g.room, request.form["message"])
        db.session.add(create_message)
        db.session.commit()
        session[str(create_message.message_id)] = str(create_message.message_id)
        return "OK!"

    messages = Message.query.filter_by(room_id=g.room.room_id).all()
    return render_template('room.html', room=roomname, messages=messages)

@app.route("/new_messages")
def get_messages():
    temp = list()
    messages = Message.query.filter_by(room_id=session['chatroom']).all()
    for message in messages:
        text = message.message_id
        if str(text) not in session:
            temp.append(message.text)
            session[str(text)] = str(text)

    return json.dumps(temp)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user is None:
            error = 'Invalid username'
        elif request.form['password'] != user.password:
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = user.user_id
            return redirect(url_for('chat'))
        return render_template('login.html', error=error)
    else:
        return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['password']:
            error = 'You have to enter a password'
        else:
            db.session.add(User(request.form['username'], request.form['password']))
            db.session.commit()
            flash('You were successfully registered')
            return render_template('layout.html')
        return render_template('register.html', error=error)
    else:
        return render_template('register.html')

@app.route('/create_room', methods=['GET', 'POST'])
def create_room():
    error = None
    if request.method == 'POST':
        db.session.add(Chatroom(request.form['topic']))
        db.session.commit()
        flash('New chatroom was successfully created')
        return redirect(url_for('chat'))
    else:
        return render_template('create_room.html')

@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    session.pop('chatroom', None)
    return redirect(url_for('chat'))

@app.route('/leave')
def leave_room():
    """Leave the room"""
    flash('You left the chatroom')
    session.pop('chatroom', None)
    return redirect(url_for('chat'))
