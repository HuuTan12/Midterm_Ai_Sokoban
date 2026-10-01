from search.ucs import UCS
from core.state import State
from core.board import Board
from core.competitive_state import CompetitiveState

class AgentHieu:
    def __init__(self):
        self.algo = UCS()
        self.name = "Agent Hiệu (UCS)"
        
    def get_action(self, comp_state: CompetitiveState, board: Board):
        # Hiệu điều khiển Agent 2
        agent_pos = comp_state.agent2_pos
        other_agent_pos = comp_state.agent1_pos

        # Kiểm tra an toàn: nếu vị trí agent chưa được đặt thì không làm gì
        if agent_pos is None:
            return None

        # Lấy danh sách các hộp chưa được đưa vào đích
        unsolved_boxes = [b for b in comp_state.all_boxes if b not in board.goals]
        if not unsolved_boxes:
            return None

        # Tìm hộp gần Agent 2 nhất
        target_box = min(unsolved_boxes, key=lambda b: abs(b[0] - agent_pos[0]) + abs(b[1] - agent_pos[1]))

        # Các hộp còn lại sẽ bị xem như bức tường để tránh đẩy nhầm
        temp_walls = set(board.walls)
        if other_agent_pos is not None:
            temp_walls.add(other_agent_pos)
            
        for b in comp_state.all_boxes:
            if b != target_box:
                temp_walls.add(b)

        temp_board = Board(board.width, board.height, temp_walls, board.goals)
        state = State(agent_pos, (target_box,))

        # Thuật toán UCS trả về path
        path, _, _, _ = self.algo.search(state, temp_board)

        if path and len(path) > 0:
            return path[0]
        return None
