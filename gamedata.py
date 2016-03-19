import random
import json

def generate_shapes(no_of_players):
  shapes = [random.randint(0, 4) for x in range(no_of_players)]
  return shapes


# Every list represents all ratings made by one player
# players are in a set order so that the first element of each list
# corresponds to a specific player's score.

# sums up an averages the results
# {"user_id": score}
def sumResults(results) :
  res = []
  for key, value in results.iteritems():
    temp = [key,round(value, 1)]
    res.append(temp)
  return res

# returns ordered [["user_id", averaged_score]]
def order(results):
  sums = sumResults(results)
  sums.sort(key=lambda x: x[1])
  return reversed(sums)




