import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.map_parser import MapParser
from search.ucs import UCS

def test_ucs_algorithm():
    map_path = os.path.join(os.path.dirname(__file__), "..", "maps", "example_map.txt")
    print(f"Loading map from: {map_path}...")

    lines = MapParser.load_map(map_path)
    board, init_state = MapParser.parse_level(lines)

    print("AI is calculating path with UCS...")
    path, cost, expanded, max_q = UCS().search(init_state, board)

    if path:
        print("\n SOLUTION FOUND!")
        print(f"Total cost: {cost}")
        print(f"Number of steps: {len(path)}")
        print(f"Action details:\n{path}")
    else:
        print("\n DEAD END: No path found!")

if __name__ == "__main__":
    test_ucs_algorithm()