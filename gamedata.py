import random

def generate_shapes():
  shapes = [random.randint(0, 4) for x in range(6)]
  return shapes


# Every list represents all ratings made by one player
# players are in a set order so that the first element of each list
# corresponds to a specific player's score.

# sums up an averages the results
def sumResults(results) :
  size = len(results)
  summed_result = [[x, 0.0] for x in range(size)]
  for L in results:
    for i in range(size) :
      summed_result[i][1] += L[i]
  for player in summed_result:
    player[1]  = round(player[1]/size, 1)
  return summed_result

# orders the results
# list of ["player_order#", "scoree"]
def order(results):
  sums = sumResults(results)
  sums.sort(key=lambda x: x[1])
  return reversed(sums)


# Call when a new score has been received
def new_score_received(gameid, teamid, score):
	pass

# Call when all scores for the given gameid have been collected
def get_game_results(gameid):
	pass