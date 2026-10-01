import unittest
import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)

from core.map_parser import MapParser
from search.bfs import BFS

class TestBFS(unittest.TestCase):
    def setUp(self):
        self.map_path = os.path.join(base_dir, "maps", "example_map.txt")
        self.lines = MapParser.load_map(self.map_path)
        self.board, self.state = MapParser.parse_level(self.lines)

    def test_bfs_search(self):
        solver = BFS()
        path, cost, expanded, max_q = solver.search(self.state, self.board)
        self.assertIsNotNone(path)
        self.assertTrue(len(path) > 0)
        self.assertTrue(cost > 0)

if __name__ == '__main__':
    unittest.main()