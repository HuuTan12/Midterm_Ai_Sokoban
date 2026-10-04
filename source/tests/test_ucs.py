import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from source.core.map_parser import MapParser
from source.search.ucs import UCS

MAP_PATH = os.path.join(os.path.dirname(__file__), '..', 'maps', 'Map1.txt')

def test_ucs_algorithm():
    print(f"Loading map from: {MAP_PATH}...")
    lines = MapParser.load_map(MAP_PATH)
    board, init_state = MapParser.parse_level(lines)

    print("AI is calculating path with UCS...")
    path, cost, expanded, max_q = UCS().search(init_state, board)

    if path:
        print("\n SOLUTION FOUND!")
        print(f"Total cost:    {cost}")
        print(f"Steps:         {len(path)}")
        print(f"Nodes expanded:{expanded}")
    else:
        print("\n DEAD END: No path found!")

if __name__ == "__main__":
    test_ucs_algorithm()