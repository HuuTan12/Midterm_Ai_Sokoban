import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import time
from source.core.map_parser import MapParser
from source.search.ucs import UCS
from source.search.astar import AStar

MAP_PATH = os.path.join(os.path.dirname(__file__), '..', 'maps', 'Map1.txt')

board, start_state = MapParser.parse_level(MapParser.load_map(MAP_PATH))

print("========== UCS ==========")
t0 = time.time()
ucs_result = UCS().search(start_state, board)
print(f"Path:     {ucs_result[0]}")
print(f"Cost:     {ucs_result[1]}")
print(f"Time:     {time.time() - t0:.4f}s")

print("\n========== A* ==========")
t0 = time.time()
astar_result = AStar().search(start_state, board)
print(f"Path:     {astar_result[0]}")
print(f"Cost:     {astar_result[1]}")
print(f"Time:     {time.time() - t0:.4f}s")