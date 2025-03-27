from stockfish import Stockfish
from flask import Flask, request
app = Flask(__name__)


@app.post('/choose_move')
def choose_move():

  data = request.json
  level = int(data.get('level'))
  elo_rating = data.get('elo_rating')
  print("Level chosen:")
  print(data.get('level'))

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

  print("Move history given: " + move_history_str)
  print("Move chosen: " + move)

  return {
    "move": move
  }

@app.post('/get_eval')
def get_eval():

  data = request.json

  stockfish = setup_stockfish(default_settings())

  move_history_str = data.get('move_history')
  stockfish.set_position(move_history_str.split(","))

  ev = stockfish.get_evaluation()

  return {
    "adv_white": map_ev(ev)
  }

@app.post('/get_eval_list')
def get_eval_list():

  data = request.json

  stockfish = setup_stockfish(default_settings())

  move_history_str = data.get('move_history')
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

def map_ev(ev):
  if ev["type"] == "cp":
    return ev["value"]
  elif ev["type"] == "mate":
    sign = 1 if ev["value"] >= 0 else -1
    return ((sign * 12) - ev["value"]) * 180
  return 0

def default_settings():
  return {
    "Debug Log File": "",
    "Contempt": 0,
    "Min Split Depth": 0,
    "Threads": 1,
    # More threads will make the engine stronger, but should be kept at less than the number of logical processors on your computer.
    "Ponder": "false",
    "Hash": 16,
    # Default size is 16 MB. It's recommended that you increase this value, but keep it as some power of 2. E.g., if you're fine using 2 GB of RAM, set Hash to 2048 (11th power of 2).
    "MultiPV": 1,
    "Move Overhead": 10,
    "Minimum Thinking Time": 20,
    "Slow Mover": 100,
    "UCI_Chess960": "false",
  }

def setup_stockfish(settings):
  return Stockfish(path="./stockfish-ubuntu-x86-64-sse41-popcnt", parameters=settings)