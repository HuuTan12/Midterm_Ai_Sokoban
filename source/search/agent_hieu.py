from search.ucs import UCS
from core.state import State
from core.board import Board
from core.competitive_state import CompetitiveState
from core.rules import Rules

class AgentHieu:
    def __init__(self):
        self.algo = UCS()
        self.name = "Agent Hieu (UCS)"
        self.path = []
        self.old_boxes = None
        self.old_pos = None

    def get_action(self, comp_state: CompetitiveState, board: Board):
        pos1 = comp_state.agent2_pos
        pos2 = comp_state.agent1_pos

        if pos1 is None:
            return None

        cur_boxes = tuple(sorted(comp_state.all_boxes))

        if self.path and self.old_boxes is not None and self.old_pos is not None:
            if cur_boxes != self.old_boxes or pos1 != self.old_pos:
                self.path = []

        if self.path:
            next_act = self.path[0]
            tmp_s = State(pos1, cur_boxes)
            bi_can = True
            for a, suc in Rules.get_successors(tmp_s, board):
                if a == next_act:
                    bi_can = (suc.agent_pos == pos2 or pos2 in suc.boxes)
                    break
            if bi_can:
                self.path = []

        if not self.path:
            tuong_gia = set(board.walls)
            if pos2 is not None:
                tuong_gia.add(pos2)
            
            fake_board = Board(board.width, board.height, tuong_gia, board.goals)
            tmp_s = State(pos1, cur_boxes)
            
            p, _, _, _ = self.algo.search(tmp_s, fake_board, timeout_seconds=1.0)
            if p:
                self.path = p
            else:
                return None

        if self.path:
            act = self.path.pop(0)
            tmp_s = State(pos1, cur_boxes)
            for a, suc in Rules.get_successors(tmp_s, board):
                if a == act:
                    self.old_boxes = suc.boxes
                    self.old_pos = suc.agent_pos
                    break
            return act

        return None
