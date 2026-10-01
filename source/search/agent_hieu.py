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

        boxes = comp_state.all_boxes

        # Biến Agent 1 thành một bức tường để Agent 2 không đi xuyên qua
        temp_walls = set(board.walls)
        if other_agent_pos is not None:
            temp_walls.add(other_agent_pos)
        temp_board = Board(board.width, board.height, temp_walls, board.goals)

        state = State(agent_pos, boxes)

        # Thuật toán UCS trả về path
        path, _, _, _ = self.algo.search(state, temp_board)

        if path and len(path) > 0:
            return path[0]
        return None
