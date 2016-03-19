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
	if(len(start_queue)%2 == 0 and len(start_queue) >= 4):
		print("new game scheduled")
		Timer(5.0, start_game, args=[start_queue[:]]).start()
	print(start_queue)
	return json.dumps({"payload": {"uid": new_user}})

@app.route('/update-game', methods=['POST'])
def update_game():
	if request.method == 'POST':
		uid = request.form['uid']
		changes = request.form['payload']
		print(changes)

	return "ok"


def start_game(users):
	sleep(5)
	if(len(users)%2 != 0 or len(users) < 4):
		return

	random.shuffle(users)
	new_game = [{"users": [users[i], users[i+1]]} for i in range(0, len(users), 2)]
	print("initiated: ", new_game)

	for g in new_game:
		pusher.trigger([g["users"][0], g["users"][1]], 'game-started', {"payload": {"shapes": gamedata.generate_shapes()}})

	global start_queue
	start_queue = list(set(start_queue)-set(users))

@app.route('/debug')
def debug():
	pusher.trigger('my-channel', 'my-event', {'message': 'hello world'})
	return "fine" 

	
if __name__ == '__main__':
	#host='0.0.0.0' only with debug disabled - security risk
	app.run(port=8080, debug=True)