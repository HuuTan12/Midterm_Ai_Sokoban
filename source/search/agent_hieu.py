import random
from source.search.ucs import UCS
from source.core.state import State
from source.core.board import Board
from source.core.competitive_state import CompetitiveState
from source.core.rules import Rules

DIRECTIONS = ["North", "South", "East", "West"]
DELTA = {"North": (-1, 0), "South": (1, 0), "West": (0, -1), "East": (0, 1)}

class AgentHieu:
    def __init__(self):
        self.algo = UCS()
        self.name = "Agent Hieu (UCS)"
        self.path = []
        self.last_pos = None
        self.stuck_count = 0

    def _valid_moves(self, agent_pos, other_pos, board):
        moves = []
        for d in DIRECTIONS:
            dr, dc = DELTA[d]
            np = (agent_pos[0] + dr, agent_pos[1] + dc)
            if not board.is_within_bounds(np) or board.is_wall(np):
                continue
            if np == other_pos:
                continue
            moves.append(d)
        return moves

    def _find_path(self, agent_pos, boxes, other_pos, board):
        temp_walls = set(board.walls)
        if other_pos is not None:
            temp_walls.add(other_pos)
        temp_board = Board(board.width, board.height, temp_walls, board.goals)
        state_obj = State(agent_pos, tuple(sorted(boxes)))
        path, _, _, _ = self.algo.search(state_obj, temp_board, timeout_seconds=0.5)
        return path or []

    def get_action(self, comp_state: CompetitiveState, board: Board):
        agent_pos = comp_state.agent2_pos
        other_pos = comp_state.agent1_pos

        if agent_pos is None:
            return None

        if agent_pos == self.last_pos:
            self.stuck_count += 1
        else:
            self.stuck_count = 0
            self.path = []
        self.last_pos = agent_pos

        if self.stuck_count >= 2:
            self.path = []
            self.stuck_count = 0
            valid = self._valid_moves(agent_pos, other_pos, board)
            return random.choice(valid) if valid else None

        if not self.path:
            my_unfinished = [b for b in comp_state.agent2_boxes if not board.is_goal(b)]
            enemy_on_goal = [b for b in comp_state.agent1_boxes if board.is_goal(b)]
            neutral = list(comp_state.neutral_boxes)

            if neutral or my_unfinished:
                self.path = self._find_path(agent_pos, list(comp_state.all_boxes), other_pos, board)
            elif enemy_on_goal:
                target = min(enemy_on_goal, key=lambda b: abs(b[0]-agent_pos[0]) + abs(b[1]-agent_pos[1]))
                steal_goals = {g for g in board.goals if g != target}
                if not steal_goals:
                    steal_goals = board.goals
                steal_board = Board(board.width, board.height, board.walls, steal_goals)
                boxes = [b for b in comp_state.all_boxes if b != target] + [target]
                self.path = self._find_path(agent_pos, boxes, other_pos, steal_board)

        if not self.path:
            valid = self._valid_moves(agent_pos, other_pos, board)
            return random.choice(valid) if valid else None

        action = self.path.pop(0)
        if hasattr(action, 'value'):
            action = action.value
        return action
