from source.core.action import Action
from source.core.state import State

class Rules:
    Directions = {
        Action.NORTH: (-1, 0),
        Action.SOUTH: (1, 0),
        Action.WEST:  (0, -1),
        Action.EAST:  (0, 1),
    }

    @staticmethod
    def get_successors(state, board):
        successors = []
        row, col = state.agent_pos

        for action, (drow, dcol) in Rules.Directions.items():
            new_row = row + drow
            new_col = col + dcol
            new_agent_pos = (new_row, new_col)

            if not board.is_within_bounds(new_agent_pos) or board.is_wall(new_agent_pos):
                continue

            if new_agent_pos in state.boxes:
                box_new_pos = (new_row + drow, new_col + dcol)
                if not board.is_within_bounds(box_new_pos) or board.is_wall(box_new_pos) or box_new_pos in state.boxes:
                    continue
                new_boxes = list(state.boxes)
                new_boxes.remove(new_agent_pos)
                new_boxes.append(box_new_pos)
                successors.append((action.value, State(new_agent_pos, new_boxes)))
            else:
                successors.append((action.value, State(new_agent_pos, state.boxes)))

        return successors