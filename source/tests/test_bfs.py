import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.map_parser import MapParser
from search.bfs import BFS

base_dir = os.path.dirname(os.path.abspath(__file__))
map_path = os.path.join(base_dir, "..", "maps", "example_map.txt")
lines = MapParser.load_map(map_path)

board, state = MapParser.parse_level(lines)

solution, cost, expanded, max_q = BFS().search(state, board)

print("=== BFS RESULT ===")

if solution is None:
    print("No solution found.")
else:
    print("Solution:", solution)
    print("Number of steps:", len(solution))