import time

from core.map_parser import MapParser
from search.ucs import ucs
from search.astar import astar


map_lines = MapParser.load_map("maps/example_map.txt")
board, start_state = MapParser.parse_level(map_lines)

print("========== UCS ==========")
ucs_result = ucs(start_state, board)

print("Path:", ucs_result[0])
print("Cost:", ucs_result[1])

print("\n========== A* ==========")
astar_result = astar(start_state, board)

print("Path:", astar_result[0])
print("Cost:", astar_result[1])