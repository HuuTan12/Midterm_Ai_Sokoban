from source.core.board import Board
from source.core.state import State

class MapParser:
    @staticmethod
    def load_map(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.rstrip('\n') for line in f]

    @staticmethod
    def parse_level(map_lines):
        walls = set()
        goals = set()
        boxes = []
        agent_pos = None
        height = len(map_lines)
        width = max((len(line) for line in map_lines), default=0)

        for row, line in enumerate(map_lines):
            for col, cell in enumerate(line):
                pos = (row, col)
                if cell == '%':
                    walls.add(pos)
                elif cell == 'D':
                    goals.add(pos)
                elif cell == 'A':
                    agent_pos = pos
                elif cell == 'B':
                    boxes.append(pos)
                elif cell == 'C':
                    boxes.append(pos)
                    goals.add(pos)

        board = Board(width=width, height=height, walls=walls, goals=goals)
        state = State(agent_pos=agent_pos, boxes=boxes)
        return board, state

    @staticmethod
    def parse_competitive_level(map_lines):
        from source.core.competitive_state import CompetitiveState
        walls = set()
        goals = set()
        boxes = []
        agent1_pos = None
        agent2_pos = None
        height = len(map_lines)
        width = max((len(line) for line in map_lines), default=0)

        for row, line in enumerate(map_lines):
            for col, cell in enumerate(line):
                pos = (row, col)
                if cell == '%':
                    walls.add(pos)
                elif cell == 'D':
                    goals.add(pos)
                elif cell == 'A':
                    agent1_pos = pos
                elif cell == 'E':
                    agent2_pos = pos
                elif cell == 'B':
                    boxes.append(pos)
                elif cell == 'C':
                    boxes.append(pos)
                    goals.add(pos)

        board = Board(width=width, height=height, walls=walls, goals=goals)
        state = CompetitiveState(agent1_pos, agent2_pos, boxes, [], [])
        return board, state
