from source.core.competitive_state import CompetitiveState


class CompetitiveRules:
    Direction_Map = {
        "North": (-1, 0),
        "South": (1,  0),
        "West":  (0, -1),
        "East":  (0,  1),
    }

    @staticmethod
    def get_next_pos(pos, action_str):
        if action_str in CompetitiveRules.Direction_Map:
            dr, dc = CompetitiveRules.Direction_Map[action_str]
            return (pos[0] + dr, pos[1] + dc)
        return pos

    @staticmethod
    def apply_actions(state: CompetitiveState, action1, action2, board):
        p1 = state.agent1_pos
        p2 = state.agent2_pos

        if p1 is None and p2 is None:
            return state

        np1 = CompetitiveRules.get_next_pos(p1, action1) if (p1 is not None and action1) else p1
        np2 = CompetitiveRules.get_next_pos(p2, action2) if (p2 is not None and action2) else p2

        d1 = CompetitiveRules.Direction_Map.get(action1, (0, 0)) if action1 else (0, 0)
        d2 = CompetitiveRules.Direction_Map.get(action2, (0, 0)) if action2 else (0, 0)

        all_boxes = set(state.all_boxes)

        def resolve_move(p, np, d, boxes_set):
            if p is None or np is None or p == np:
                return p, None
            if not board.is_within_bounds(np) or board.is_wall(np):
                return p, None
            if np in boxes_set:
                nbp = (np[0] + d[0], np[1] + d[1])
                if not board.is_within_bounds(nbp) or board.is_wall(nbp) or nbp in boxes_set:
                    return p, None
                return np, (np, nbp)
            return np, None

        np1, push1 = resolve_move(p1, np1, d1, all_boxes)
        np2, push2 = resolve_move(p2, np2, d2, all_boxes)

        if p1 is not None and p2 is not None and np1 == p2 and np2 == p1:
            np1, push1 = p1, None
            np2, push2 = p2, None

        if p1 is not None and p2 is not None and np1 == np2 and np1 != p1:
            np2, push2 = p2, None

        if push1 and p2 is not None and push1[1] == np2:
            np2, push2 = p2, None
        if push2 and p1 is not None and push2[1] == np1:
            np1, push1 = p1, None

        if push1 and push2 and push1[1] == push2[1]:
            np2, push2 = p2, None

        if p1 is not None and p2 is not None and np1 == np2 and np1 != p1:
            np2, push2 = p2, None

        neutral_boxes = list(state.neutral_boxes)
        agent1_boxes  = list(state.agent1_boxes)
        agent2_boxes  = list(state.agent2_boxes)

        def apply_push(old_pos, new_pos, owner_id):
            if old_pos in neutral_boxes:
                neutral_boxes.remove(old_pos)
            elif old_pos in agent1_boxes:
                agent1_boxes.remove(old_pos)
            elif old_pos in agent2_boxes:
                agent2_boxes.remove(old_pos)

            if owner_id == 1:
                agent1_boxes.append(new_pos)
            elif owner_id == 2:
                agent2_boxes.append(new_pos)
            else:
                neutral_boxes.append(new_pos)

        if push1:
            apply_push(push1[0], push1[1], 1)
        if push2:
            apply_push(push2[0], push2[1], 2)

        return CompetitiveState(np1, np2, neutral_boxes, agent1_boxes, agent2_boxes)
