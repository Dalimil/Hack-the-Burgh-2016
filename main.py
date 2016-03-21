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
GAME_SIZE = 2 # should be 6
TEAM_SIZE = 1 # should be 2
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
	pusher.trigger(teams[teamid]["users"], "game-updated", {"payload": shapes})
	return "ok"

tries = 0
@app.route('/finish', methods=['POST'])
def finish_game():
	print("called finished")
	data  = request.get_json()
	print("finish: ", data)
	uid = data['uid']
	img_name = data['name']

	if not users.has_key(uid):
		print("error", users)
		return "error"

	teamid = users[uid]
	game_states[teamid]["phase"] = "stopped"
	print(teams[teamid]["gameid"])
	if(game_states[teamid].has_key("img_name")):
		game_states[teamid]["img_name"] += " "+img_name
	else:
		game_states[teamid]["img_name"] = img_name

	print(teams[teamid]["users"])
	global tries
	tries = 0
	pusher.trigger(teams[teamid]["users"], "game-finished", {"payload": "game-finished"})
	sleep(2)
	return json.dumps({"payload": check_game_over(teams[teamid]["gameid"])}) # this should be made async with Pusher

@app.route('/rate', methods=['POST'])
def rate_game():
	teamid = request.form['teamid']
	score = request.form['score']
	gameid = teams[teamid]["gameid"]
	gamedata.new_score_received(gameid, teamid, score)

	if(game_ratings[gameid] >= (TEAM_SIZE - 1)*(TEAM_SIZE)):
		send_game_results(gameid)
	return "ok"


def check_game_over(gameid):
	print("checking game over ")
	is_over = True
	for t in games[gameid]:
		if(game_states[t]["phase"] != "stopped"):
			is_over = False
	print("checking game over ", is_over)
	if is_over:
		players = get_all_players(gameid)
		game_products = get_game_products(gameid)
		print("sent products", game_products)
		print(players)
		return game_products
	else:
		print("I'll try later")
		global tries
		tries += 1
		if(tries > 3):
			return get_game_products(gameid)
		sleep(2)
		return check_game_over(gameid)

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
		Timer(3.0, start_game, args=[start_queue[:GAME_SIZE]]).start()
		return True
	return False

def start_game(participants):
	random.shuffle(participants)
	new_game = [{"users": [participants[j] for j in range(i, i+TEAM_SIZE)]} for i in range(0, len(participants), TEAM_SIZE)]
	print("initiated: ", new_game)

	new_shapes = gamedata.generate_shapes()

	for g in new_game:
		print(g["users"])
		pusher.trigger(g["users"], 'game-started', {"payload": {"shapes": new_shapes}})

	global start_queue, schedule_lock
	start_queue = list(set(start_queue)-set(participants))
	schedule_lock = False

	global games, teams, users
	new_teams = []
	new_gameid = generate_game_id()
	for i in range(0, len(participants), TEAM_SIZE):
		new_team = generate_team_id()
		uss = [participants[j] for j in range(i, i+TEAM_SIZE)]
		for i in uss:
			users[i] = new_team
		teams[new_team] = {"users":uss, "gameid": new_gameid}
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
	app.run(port=8080)
