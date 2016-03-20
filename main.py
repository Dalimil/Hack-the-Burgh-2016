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
app.secret_key = "bnNoqxXSgzoXS3j4v3v3zv8nRzn"

start_queue = []
schedule_lock = False
GAME_SIZE = 2
games = {} # <gameid, list(channelids)>
teams = {} # <channelid, <list(userids), gameid> >
users = {} # <userid, channelid>

game_states = {} # indexed by teamid
game_ratings = {} # counts indexed by gameid

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

@app.route('/update', methods=['POST'])
def update_game():
	data  = request.get_json()
	uid = data['uid']
	shapes = data['shapes']
	
	if not users.has_key(uid):
		return "error"

	teamid = users[uid]
	print(uid, shapes)
	game_states[teamid]["config"] = shapes
	return "ok"

@app.route('/finish', methods=['POST'])
def finish_game():
	data  = request.get_json()
	uid = data['uid']
	img_name = data['name']

	if not users.has_key(uid):
		return "error"

	teamid = users[uid]
	game_states[teamid]["phase"] = "stopped"
	game_states[teamid]["img_name"] = img_name
	pusher.trigger(teams[teamid]["users"], "game-finished", {"payload": "game-finished"})
	Timer(2.0, check_game_over, args=[teams[teamid]["gameid"]]).start()
	return "ok"

@app.route('/rate', methods=['POST'])
def rate_game():
	teamid = request.form['teamid']
	score = request.form['score']
	gameid = teams[teamid]["gameid"]
	gamedata.new_score_received(gameid, teamid, score)

	if(game_ratings[gameid] >= (GAME_SIZE//2 - 1)*(GAME_SIZE//2)):
		send_game_results(gameid)
	return "ok"

def check_game_over(gameid):
	is_over = all(game_states[t]["phase"] == "stopped" for t in games[gameid])
	if is_over:
		players = get_all_players(gameid)
		pusher.trigger(players, 'game-products', {"payload": get_game_products(gameid)})

def get_all_players(gameid):
	players = []
	for t in games[gameid]:
		players += teams[t]["users"]
	return players

def get_game_products(gameid):
	return [{"config": game_states[t]["config"], "name": game_states[t]["img_name"]} for t in games[gameid]]

def send_game_results():
	results = gamedata.get_game_results(gameid)
	players = get_all_players(gameid)
	pusher.trigger(players, 'game-results', {"payload": results})

def check_start_game():
	global schedule_lock, start_queue
	if(len(start_queue) >= GAME_SIZE and not schedule_lock):
		print("new game scheduled")
		schedule_lock = True
		Timer(5.0, start_game, args=[start_queue[:GAME_SIZE]]).start()
		return True
	return False

def start_game(participants):
	random.shuffle(participants)
	new_game = [{"users": [participants[i], participants[i+1]]} for i in range(0, len(participants), 2)]
	print("initiated: ", new_game)

	for g in new_game:
		print(g["users"][0], g["users"][1])
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
		game_states[new_team] = {"phase":"running", "config": None}
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
