from flask import Flask
from flask import render_template, request, redirect, session, url_for, escape, make_response, flash, abort
from pusher import Pusher
import random
import json
import thread
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


def generate_channel_id():
	return "game-glob-ch-"+ str(random.randint(10000, 90000))

def generate_game_id():
	return "game-loc-ch-" + str(random.randint(10000, 90000))

def generate_user_id():
	return "uid-" + str(random.randint(10000, 90000))

@app.route('/')
def index():
	return render_template('demo.html')

@app.route('/join')
def join():
	global start_queue
	user_count = len(users)
	if(len(start_game)%2 == 0 and len(start_queue) >= 4):
		thread.start_new_thread(start_game, ())

	new_user = generate_user_id()
	start_queue.append(new_user)
	return json.dumps({"payload": {"uid": new_user}})

#channel = pusher.channel_info(u'start-queue', [u"user_count"])

@app.route('/update-game')
def update_game():
	return "ok"

@app.route('/debug')
def debug():
	pusher.trigger('my-channel', 'my-event', {'message': 'hello world'})
	return "fine" 


def start_game():
	sleep(5)
	random.shuffle(start_queue)
	new_game_id = generate_game_id()
	new_game = [{"local-channel-id": generate_channel_id(), 
				"global-channel-id": new_game_id, 
				"users": [users[i]['id'], users[i+1]['id']]} for i in range(0, len(users), 2)]
	pusher.trigger('start-queue', 'game-started', {"payload": new_game})

if __name__ == '__main__':
	#host='0.0.0.0' only with debug disabled - security risk
	app.run(port=8080, debug=True)