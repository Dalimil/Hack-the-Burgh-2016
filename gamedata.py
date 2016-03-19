import random
import json

scores = {} # <gameid, <userid, score>>

def generate_shapes():
	shapes = [random.randint(0, 4) for x in range(6)]
	return shapes


# Every list represents all ratings made by one player
# players are in a set order so that the first element of each list
# corresponds to a specific player's score.

# sums up an averages the results
# {"user_id": score}
def sumResults(results):
	res = []
	size = len(results)
	for key, value in results.iteritems():
		temp = [key,round(value*1.0/size, 1)]
		res.append(temp)
	return res

# returns ordered [["user_id", averaged_score]]
def order(results):
	sums = sumResults(results)
	sums.sort(key=lambda x: x[1])
	return reversed(sums)

# Call when a new score has been received
def new_score_received(gameid, teamid, score):
	if scores.has_key(gameid):
		if scores[gameid].has_key(teamid):
			scores[gameid][teamid] += score
		else:
			scores[gameid][teamid] = score
	else:
		scores[gameid] = {}
		scores[gameid][teamid] = score

# Call when all scores for the given gameid have been collected
def get_game_results(gameid):
	return order(scores[gameid])
