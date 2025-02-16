from stockfish import Stockfish
from flask import Flask, request
app = Flask(__name__)


@app.post('/choose_move')
def choose_move():

  data = request.json
  level = int(data.get('level'))

  # Setup Stockfish
  settings = {
    "Debug Log File": "",
    "Contempt": 0,
    "Min Split Depth": 0,
    "Threads": 1,
    # More threads will make the engine stronger, but should be kept at less than the number of logical processors on your computer.
    "Ponder": "false",
    "Hash": 16,
    # Default size is 16 MB. It's recommended that you increase this value, but keep it as some power of 2. E.g., if you're fine using 2 GB of RAM, set Hash to 2048 (11th power of 2).
    "MultiPV": 1,
    "Skill Level": level,
    "Move Overhead": 10,
    "Minimum Thinking Time": 20,
    "Slow Mover": 100,
    "UCI_Chess960": "false",
  }
  stockfish = Stockfish(path="./stockfish-ubuntu-x86-64-sse41-popcnt", parameters=settings)

  # Setup pieces with given move history
  move_history = data.get('move_history').split(",")
  stockfish.set_position(move_history)

  return {
    "move": stockfish.get_best_move()
  }