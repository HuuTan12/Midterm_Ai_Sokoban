
from source.search.astar import AStar
from source.search.ucs import UCS
from source.core.state import State
from source.core.board import Board
from source.core.competitive_state import CompetitiveState
from source.core.rules import Rules


class SmartAgent:
    def __init__(self, algo_class, name, agent_id):
        self.algo = algo_class()
        self.name = name
        self.agent_id = agent_id
        self.path = []
        self.expected_boxes = None

    def get_action(self, comp_state: CompetitiveState, board: Board):
        agent_pos = comp_state.agent1_pos if self.agent_id == 1 else comp_state.agent2_pos
        other_agent_pos = comp_state.agent2_pos if self.agent_id == 1 else comp_state.agent1_pos

        if agent_pos is None:
            return None

        current_boxes = tuple(sorted(comp_state.all_boxes))
        
        # 1. Check if we need to replan due to unexpected box changes
        if self.path and self.expected_boxes is not None:
            if current_boxes != self.expected_boxes:
                self.path = []

        # 2. Check if the next step is blocked by the other agent
        if self.path:
            next_action = self.path[0]
            state_obj = State(agent_pos, current_boxes)
            blocked = True
            for act_val, succ_state in Rules.get_successors(state_obj, board):
                if act_val == next_action:
                    # Hitting other agent directly?
                    if succ_state.agent_pos == other_agent_pos:
                        blocked = True
                    # Pushing a box into the other agent?
                    elif other_agent_pos in succ_state.boxes:
                        blocked = True
                    else:
                        blocked = False
                    break
            
            if blocked:
                self.path = []

        # 3. Replan if needed
        if not self.path:
            temp_walls = set(board.walls)
            if other_agent_pos is not None:
                temp_walls.add(other_agent_pos)
            temp_board = Board(board.width, board.height, temp_walls, board.goals)
            state_obj = State(agent_pos, current_boxes)
            
            path, _, _, _ = self.algo.search(state_obj, temp_board, timeout_seconds=1.0)
            if path and len(path) > 0:
                self.path = path
            else:
                return None

        # 4. Execute the next action
        if self.path:
            action_to_take = self.path.pop(0)
            
            state_obj = State(agent_pos, current_boxes)
            for act_val, succ_state in Rules.get_successors(state_obj, board):
                if act_val == action_to_take:
                    self.expected_boxes = succ_state.boxes
                    break
                    
            return action_to_take
            
        return None
