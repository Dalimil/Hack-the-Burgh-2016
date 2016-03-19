import random

def newGame() :
  shapes = [random.randint(0, 4) for x in range(6)]
  return shapes
