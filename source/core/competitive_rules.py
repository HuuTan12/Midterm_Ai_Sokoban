from source.core.action import Action
from source.core.competitive_state import CompetitiveState

class CompetitiveRules:
    Direction_Map = {
        "North": (-1, 0),
        "South": (1, 0),
        "West": (0, -1),
        "East": (0, 1)
    }

    @staticmethod
    def get_next_pos(pos, action_str):
        if action_str in CompetitiveRules.Direction_Map:
            dr, dc = CompetitiveRules.Direction_Map[action_str]
            return (pos[0] + dr, pos[1] + dc)
        return pos

    @staticmethod
    def apply_actions(state: CompetitiveState, action1: str, action2: str, board):
        p1 = state.agent1_pos
        p2 = state.agent2_pos

        if p1 is None and p2 is None:
            return state

        np1 = CompetitiveRules.get_next_pos(p1, action1) if p1 is not None else None
        np2 = CompetitiveRules.get_next_pos(p2, action2) if p2 is not None else None

        all_boxes = set(state.all_boxes)

        box_push1 = None
        box_push2 = None

        def check_move(p, np, d, other_p):
            if p is None or np is None:
                return p, None
            if not board.is_within_bounds(np) or board.is_wall(np):
                return p, None

            box_push = None
            if np in all_boxes:
                nbp = (np[0] + d[0], np[1] + d[1])
                if not board.is_within_bounds(nbp) or board.is_wall(nbp) or nbp in all_boxes:
                    return p, None
                box_push = (np, nbp)
            return np, box_push

        d1 = CompetitiveRules.Direction_Map.get(action1, (0, 0))
        d2 = CompetitiveRules.Direction_Map.get(action2, (0, 0))

        np1, box_push1 = check_move(p1, np1, d1, p2)
        np2, box_push2 = check_move(p2, np2, d2, p1)

        if np1 == np2:
            np1, box_push1 = p1, None
            np2, box_push2 = p2, None

        if np1 == p2 and np2 == p1:
            np1, box_push1 = p1, None
            np2, box_push2 = p2, None

        if box_push1 and box_push1[1] == np2:
            np1, box_push1 = p1, None
            np2, box_push2 = p2, None

        if box_push2 and box_push2[1] == np1:
            np1, box_push1 = p1, None
            np2, box_push2 = p2, None

        if box_push1 and box_push2 and box_push1[1] == box_push2[1]:
            np1, box_push1 = p1, None
            np2, box_push2 = p2, None

        neutral_boxes = list(state.neutral_boxes)
        agent1_boxes = list(state.agent1_boxes)
        agent2_boxes = list(state.agent2_boxes)

        def update_box(old_pos, new_pos, owner_id):
            if old_pos in neutral_boxes: neutral_boxes.remove(old_pos)
            if old_pos in agent1_boxes: agent1_boxes.remove(old_pos)
            if old_pos in agent2_boxes: agent2_boxes.remove(old_pos)

            if owner_id == 1:
                agent1_boxes.append(new_pos)
            elif owner_id == 2:
                agent2_boxes.append(new_pos)

        if box_push1:
            update_box(box_push1[0], box_push1[1], 1)
        if box_push2:
            update_box(box_push2[0], box_push2[1], 2)

        return CompetitiveState(np1, np2, neutral_boxes, agent1_boxes, agent2_boxes)
