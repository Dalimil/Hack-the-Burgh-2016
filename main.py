from flask import Flask
from flask import render_template, request, redirect, session, url_for, escape, make_response, flash, abort
from pusher import Pusher
import random
import json
import gamedata
from threading import Timer
from time import sleep

pusher = Pusher(
  app_id='189177',
  key='fb45d9e64fdf2db64ed2',
  secret='1ba32d9ad91822e34883'
)

app = Flask(__name__)
# (session encryption) keep this really secret:
app.secret_key = "bnNoqxXSgzoXSOezxpZjb8mrMp5L0L4mJ4o8nRzn"

start_queue = []

def generate_game_id():
	return "game-ch-" + str(random.randint(10000, 90000))

def generate_user_id():
	return "uid-" + str(random.randint(10000, 90000))

@app.route('/')
def index():
	return render_template('demo.html')

@app.route('/join')
def join():
	global start_queue
	new_user = generate_user_id()
	start_queue.append(new_user)
	user_count = len(users)
	if(len(start_game)%2 == 0 and len(start_queue) >= 4):
		Timer(5.0, start_game).start()
	return json.dumps({"payload": {"uid": new_user}})

@app.route('/update-game')
def update_game():
	return "ok"

@app.route('/debug')
def debug():
	pusher.trigger('my-channel', 'my-event', {'message': 'hello world'})
	return "fine" 


def start_game():
	sleep(5)
	if(len(start_queue)%2 != 0 or len(start_queue) < 4):
		return

	random.shuffle(start_queue)
	new_game = [{"users": [users[i]['id'], users[i+1]['id']]} for i in range(0, len(start_queue), 2)]

	for g in new_game:
		pusher.trigger([g["users"][0], g["users"][1]], 'game-started', {"payload": {"shapes": gamedata.generate_shapes()}})


if __name__ == '__main__':
	#host='0.0.0.0' only with debug disabled - security risk
	app.run(port=8080, debug=True)