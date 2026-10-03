import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.map_parser import MapParser
from core.rules import Rules

base_dir = os.path.dirname(os.path.abspath(__file__))
map_path = os.path.join(base_dir, "..", "maps", "example_map.txt")
lines = MapParser.load_map(map_path)

board, state = MapParser.parse_level(lines)

print("=== BOARD ===")
print("Width:", board.width)
print("Height:", board.height)
print("Walls:", board.walls)
print("Goals:", board.goals)

print("\n=== STATE ===")
print("Agent:", state.agent_pos)
print("Boxes:", state.boxes)

successors = Rules.get_successors(state, board)

print("\n=== SUCCESSORS ===")

for action, new_state in successors:
    print("Action:", action)
    print("Agent:", new_state.agent_pos)
    print("Boxes:", new_state.boxes)
    print("---")