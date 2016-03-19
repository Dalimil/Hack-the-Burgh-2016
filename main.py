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
schedule_lock = False
GAME_SIZE = 4
games = {} # <gameid, list(channelids)>
teams = {} # <channelid, <list(userids), gameid> >
users = {} # <userid, channelid>

def generate_game_id():
	return "gameid-" + str(random.randint(10000, 90000))

def generate_team_id():
	return "teamid-" + str(random.randint(10000, 90000))

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
	print(start_queue)
	check_start_game()
	return json.dumps({"payload": {"uid": new_user}})

@app.route('/update-game', methods=['POST'])
def update_game():
	if request.method == 'POST':
		uid = request.form['uid']
		changes = request.form['payload']
		print(changes)

	return "ok"


def check_start_game():
	global schedule_lock, start_queue
	if(len(start_queue) >= GAME_SIZE and not schedule_lock):
		print("new game scheduled")
		schedule_lock = True
		Timer(5.0, start_game, args=[start_queue[:GAME_SIZE]]).start()
		return True
	return False

def start_game(participants):
	sleep(5)
	random.shuffle(participants)
	new_game = [{"users": [participants[i], participants[i+1]]} for i in range(0, len(participants), 2)]
	print("initiated: ", new_game)

	for g in new_game:
		pusher.trigger([g["users"][0], g["users"][1]], 'game-started', {"payload": {"shapes": gamedata.generate_shapes()}})

	global start_queue, schedule_lock
	start_queue = list(set(start_queue)-set(participants))
	schedule_lock = False

	global games, teams, users
	new_teams = []
	new_gameid = generate_game_id()
	for i in range(0, len(participants), 2):
		new_team = generate_team_id()
		ua = participants[i]
		ub = participants[i+1]
		users[ua] = new_team
		users[ub] = new_team
		teams[new_team] = {"users":[ua, ub], "gameid": new_gameid}
		new_teams.append(new_team)
	games[new_gameid] = new_teams
	print(games, teams, users)
	check_start_game()


@app.route('/debug')
def debug():
	pusher.trigger('my-channel', 'my-event', {'message': 'hello world'})
	print(games, teams, users)
	return "fine" 


if __name__ == '__main__':
	#host='0.0.0.0' only with debug disabled - security risk
	app.run(port=8080, debug=True)