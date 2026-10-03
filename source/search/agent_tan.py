from search.astar import AStar
from core.state import State
from core.board import Board
from core.competitive_state import CompetitiveState
from core.rules import Rules

class AgentTan:
    def __init__(self):
        self.algo = AStar()
        self.name = "Agent Tan (A*)"
        self.path = []
        self.expected_boxes = None

    def get_action(self, comp_state: CompetitiveState, board: Board):
        agent_pos = comp_state.agent1_pos
        other_pos = comp_state.agent2_pos

        if agent_pos is None:
            return None

        current_boxes = tuple(sorted(comp_state.all_boxes))

        if self.path and self.expected_boxes is not None:
            if current_boxes != self.expected_boxes:
                self.path = []

        if self.path:
            next_action = self.path[0]
            state_obj = State(agent_pos, current_boxes)
            blocked = True
            for act, succ in Rules.get_successors(state_obj, board):
                if act == next_action:
                    blocked = (succ.agent_pos == other_pos or other_pos in succ.boxes)
                    break
            if blocked:
                self.path = []

        if not self.path:
            temp_walls = set(board.walls)
            if other_pos is not None:
                temp_walls.add(other_pos)
            temp_board = Board(board.width, board.height, temp_walls, board.goals)
            state_obj = State(agent_pos, current_boxes)
            path, _, _, _ = self.algo.search(state_obj, temp_board, timeout_seconds=30.0)
            if path:
                self.path = path
            else:
                return None

        if self.path:
            action = self.path.pop(0)
            state_obj = State(agent_pos, current_boxes)
            for act, succ in Rules.get_successors(state_obj, board):
                if act == action:
                    self.expected_boxes = succ.boxes
                    break
            return action

        return None
