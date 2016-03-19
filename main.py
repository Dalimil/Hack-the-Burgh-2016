from flask import Flask
from flask import render_template, request, redirect, session, url_for, escape, make_response, flash, abort
import database

app = Flask(__name__)
# (session encryption) keep this really secret:
app.secret_key = "bnNoqxXSgzoXSOezxpZjb8mrMp5L0L4mJ4o8nRzn"

# SQL Alchemy database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db' # absolute
# also possible "mysql://username:password@server/db" (or postgresql)
database.db.init_app(app) # bind
database.db.create_all(app=app) # create tables

@app.route('/')
def index():
	return "OK"

# Flask-SocketIO -------------------------------------------------------
@app.route('/socket_index')
def my_socket_page():
	return render_template('sockets_example.html')

from flask_socketio import SocketIO, send, emit
# WebSockets setup -- "https://flask-socketio.readthedocs.org/en/latest/"
# See docs for 'rooms' - join/leave etc.
socketio = SocketIO(app)
# SocketIO RECEIVE and SEND Messages
# Originating from a user
@socketio.on('user_clicked_button') # CUSTOM or use predefined 'json', or 'message' (for strings)
def handle_my_custom_event(arg1, arg2): # any number of args
    print(arg1); print(arg2)
    print(session)
    emit('all_ok', "You sent me this:"+arg2) # broadcast=True

# Originating from this server
def some_internal_function():
	# different emit()/send() (notice 'socketio' prefix)
    socketio.emit('big_news', {'data': 42}) # broadcast is implicit

# -------------------------------------------------------------------

if __name__ == '__main__':
	#host='0.0.0.0' only with debug disabled - security risk
	#app.run(port=8080, debug=True) - don't use this one with sockets
	socketio.run(app, port=8080, debug=True) # only use this with sockets