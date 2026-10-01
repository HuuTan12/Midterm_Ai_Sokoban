from search.astar import AStar
from core.state import State
from core.board import Board
from core.competitive_state import CompetitiveState
from core.rules import Rules

class AgentTan:
    def __init__(self):
        self.algo = AStar()
        self.name = "Agent Tân (A*)"
        
    def get_action(self, comp_state: CompetitiveState, board: Board):
        # Tân điều khiển Agent 1
        agent_pos = comp_state.agent1_pos
        other_agent_pos = comp_state.agent2_pos

        # Kiểm tra an toàn: nếu vị trí agent chưa được đặt thì không làm gì
        if agent_pos is None:
            return None

        # Lấy danh sách các hộp chưa được đưa vào đích
        unsolved_boxes = [b for b in comp_state.all_boxes if b not in board.goals]
        if not unsolved_boxes:
            return None

        # Tìm hộp gần Agent 1 nhất
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

        # Thuật toán A* trả về path (chạy siêu nhanh < 0.01s nhờ đã thu gọn mục tiêu)
        path, _, _, _ = self.algo.search(state, temp_board)

        if path and len(path) > 0:
            return path[0]
        return None
