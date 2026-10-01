from search.ucs import UCS
from core.state import State
from core.board import Board
from core.competitive_state import CompetitiveState
from core.rules import Rules

class AgentHieu:
    def __init__(self):
        self.algo = UCS()
        self.name = "Agent Hiệu (UCS)"
        self.path = []
        self.expected_boxes = None

    def get_action(self, comp_state: CompetitiveState, board: Board):
        agent_pos = comp_state.agent2_pos
        other_agent_pos = comp_state.agent1_pos

        if agent_pos is None:
            return None

        current_boxes = tuple(sorted(comp_state.all_boxes))
        
        # 1. Kiểm tra có cần tính lại đường đi nếu hộp bị thay đổi ngoài dự kiến
        if self.path and self.expected_boxes is not None:
            if current_boxes != self.expected_boxes:
                self.path = []

        # 2. Kiểm tra bước tiếp theo có bị đụng Agent kia không
        if self.path:
            next_action = self.path[0]
            state_obj = State(agent_pos, current_boxes)
            blocked = True
            for act_val, succ_state in Rules.get_successors(state_obj, board):
                if act_val == next_action:
                    # Đụng trực tiếp vào vị trí Agent kia
                    if succ_state.agent_pos == other_agent_pos:
                        blocked = True
                    # Hoặc đẩy hộp vào vị trí Agent kia
                    elif other_agent_pos in succ_state.boxes:
                        blocked = True
                    else:
                        blocked = False
                    break
            
            if blocked:
                self.path = []

        # 3. Tính toán lại đường đi nếu cần
        if not self.path:
            # Biến Agent kia thành bức tường tạm thời
            temp_walls = set(board.walls)
            if other_agent_pos is not None:
                temp_walls.add(other_agent_pos)
            temp_board = Board(board.width, board.height, temp_walls, board.goals)
            state_obj = State(agent_pos, current_boxes)
            
            path, _, _, _ = self.algo.search(state_obj, temp_board, timeout_seconds=5.0)
            if path and len(path) > 0:
                self.path = path
            else:
                return None

        # 4. Thực thi bước tiếp theo và dự đoán vị trí hộp
        if self.path:
            action_to_take = self.path.pop(0)
            
            state_obj = State(agent_pos, current_boxes)
            for act_val, succ_state in Rules.get_successors(state_obj, board):
                if act_val == action_to_take:
                    self.expected_boxes = succ_state.boxes
                    break
                    
            return action_to_take
            
        return None
