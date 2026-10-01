import unittest
import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)

from core.map_parser import MapParser
from core.rules import Rules

class TestCore(unittest.TestCase):
    def setUp(self):
        self.map_path = os.path.join(base_dir, "maps", "example_map.txt")
        self.lines = MapParser.load_map(self.map_path)
        self.board, self.state = MapParser.parse_level(self.lines)

    def test_parse_level(self):
        self.assertTrue(self.board.width > 0)
        self.assertTrue(self.board.height > 0)
        self.assertTrue(len(self.board.walls) > 0)
        self.assertTrue(len(self.board.goals) > 0)
        self.assertIsNotNone(self.state.agent_pos)
        self.assertTrue(len(self.state.boxes) > 0)

    def test_get_successors(self):
        successors = Rules.get_successors(self.state, self.board)
        self.assertIsInstance(successors, list)

if __name__ == '__main__':
    unittest.main()