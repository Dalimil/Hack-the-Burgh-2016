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
