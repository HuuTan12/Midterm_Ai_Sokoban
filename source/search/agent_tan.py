from search.astar import AStar
from core.state import State
from core.board import Board
from core.competitive_state import CompetitiveState

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

        boxes = comp_state.all_boxes

        # Biến Agent 2 thành một bức tường để Agent 1 không đi xuyên qua
        temp_walls = set(board.walls)
        if other_agent_pos is not None:
            temp_walls.add(other_agent_pos)
        temp_board = Board(board.width, board.height, temp_walls, board.goals)

        state = State(agent_pos, boxes)

        # Thuật toán A* trả về path
        path, _, _, _ = self.algo.search(state, temp_board)

        if path and len(path) > 0:
            return path[0]
        return None
