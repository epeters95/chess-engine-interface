from stockfish import Stockfish
from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
app = Flask(__name__)

# Add rate limiter for API

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["30 per minute", "1 per second"],
    storage_uri="memory://",
    # Redis
    # storage_uri="redis://localhost:6379",
    # Redis cluster
    # storage_uri="redis+cluster://localhost:7000,localhost:7001,localhost:70002",
    # Memcached
    # storage_uri="memcached://localhost:11211",
    # Memcached Cluster
    # storage_uri="memcached://localhost:11211,localhost:11212,localhost:11213",
    # MongoDB
    # storage_uri="mongodb://localhost:27017",
    strategy="fixed-window", # or "moving-window", or "sliding-window-counter"
)


# Get the best move given a position and skill level
# Params:
#   level - the stockfish skill level (1-20)
#   elo_rating - the desired elo rating to emulate (0-3200)
#   move_history - comma-separated list of moves denoted by UCI
@app.post('/choose_move')
def choose_move():

  data = request.json
  level = int(data.get('level'))
  elo_rating = data.get('elo_rating')
  print(f"Level chosen: {level}")
  print(f"Elo chosen: {elo_rating}")

  # Setup Stockfish
  settings = default_settings()
  settings["Skill Level"] = level
  stockfish = setup_stockfish(settings)

  if elo_rating:
    stockfish.set_elo_rating(int(elo_rating))

  # Setup pieces with given move history
  move_history_str = data.get('move_history')
  stockfish.set_position(move_history_str.split(","))
  move = stockfish.get_best_move()

  print(f"Move history given: {move_history_str}")
  print(f"Move chosen: {move}")

  return {
    "move": move
  }

# Get the estimated advantage for white in centipawns, given a position
# Params
#   move_history - moves played so far in comma-separated UCI
# Returns
#   JSON object e.g. { "adv_white": 3 }
@app.post('/get_eval')
def get_eval():

  data = request.json

  stockfish = setup_stockfish(default_settings())

  move_history_str = data.get('move_history')
  stockfish.set_position(move_history_str.split(","))

  print(f"Evaluating position for move history: {move_history_str}")

  ev = stockfish.get_evaluation()

  print(f"Evaluated advantage white: {map_ev(ev)}")

  return {
    "adv_white": map_ev(ev)
  }

# Get the advantage white evaluation for each move in a list
# Params
#   - move_history - moves played so far in comma-separated UCI
# Returns
#   JSON object e.g. { "move_evals": [ { "adv_white": 3 }, ... ] }
@app.post('/get_eval_list')
def get_eval_list():

  data = request.json

  stockfish = setup_stockfish(default_settings())

  move_history_str = data.get('move_history')

  print(f"Evaluating all positions for move history: {move_history_str}")

  moves_remaining = move_history_str.split(",")
  moves_remaining.reverse()

  moves_sofar = []
  evals = []


  while len(moves_remaining) > 0:
    moves_sofar.append(moves_remaining[-1])
    moves_remaining.pop()
    stockfish.set_position(moves_sofar)
    evals.append(stockfish.get_evaluation())

  move_evals = list(map(map_ev, evals))

  return {
    "move_evals": move_evals
  }

# Helper function to "normalize" the evaluation units to centipawn values
# If there is mate in x moves, the centipawn advantage is substantial
def map_ev(ev):
  if ev["type"] == "cp":
    return ev["value"]
  elif ev["type"] == "mate":
    sign = 1 if ev["value"] >= 0 else -1
    return ((sign * 12) - ev["value"]) * 180
  return 0


# Test endpoint to check if the service is running
@app.get('/status')
def get_status():

  try:
    stockfish = setup_stockfish(default_settings())

    if (stockfish):
      return {
        "status": "ok"
      }

  except:
    return {
      "status": "error"
    }

# Settings for Python Stockfish library
def default_settings():
  return {
    "Debug Log File": "",
    "Contempt": 0,
    "Min Split Depth": 0,
    "Threads": 1,
    # More threads will make the engine stronger, but should be kept at less than the number of logical processors on your computer.
    "Ponder": "false",
    "Hash": 64,
    # Default size is 16 MB. It's recommended that you increase this value, but keep it as some power of 2. E.g., if you're fine using 2 GB of RAM, set Hash to 2048 (11th power of 2).
    "MultiPV": 1,
    "Move Overhead": 10,
    "Minimum Thinking Time": 40,
    "Slow Mover": 100,
    "UCI_Chess960": "false",
  }

def setup_stockfish(settings):
  return Stockfish(path="./stockfish-ubuntu-x86-64-sse41-popcnt", parameters=settings)