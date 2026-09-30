from core.action import Action
from core.competitive_state import CompetitiveState

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
        # Lấy trạng thái hiện tại
        p1 = state.agent1_pos
        p2 = state.agent2_pos
        
        np1 = CompetitiveRules.get_next_pos(p1, action1)
        np2 = CompetitiveRules.get_next_pos(p2, action2)
        
        all_boxes = set(state.all_boxes)
        
        # Tính toán việc đẩy hộp
        box_push1 = None # (from, to)
        box_push2 = None
        
        # Hàm kiểm tra hợp lệ cơ bản (không tính va chạm với agent khác)
        def check_move(p, np, d, other_p):
            if not board.is_within_bounds(np) or board.is_wall(np):
                return p, None # Không đi được
            
            box_push = None
            if np in all_boxes:
                # Muốn đẩy hộp
                nbp = (np[0] + d[0], np[1] + d[1])
                # Hộp bị kẹt nếu đụng tường, ngoài map, hoặc đụng hộp khác
                if not board.is_within_bounds(nbp) or board.is_wall(nbp) or nbp in all_boxes:
                    return p, None
                box_push = (np, nbp)
            return np, box_push

        d1 = CompetitiveRules.Direction_Map.get(action1, (0,0))
        d2 = CompetitiveRules.Direction_Map.get(action2, (0,0))
        
        np1, box_push1 = check_move(p1, np1, d1, p2)
        np2, box_push2 = check_move(p2, np2, d2, p1)
        
        # Xử lý va chạm đồng thời
        # 1. Đổi chỗ (swap)
        if np1 == p2 and np2 == p1:
            np1, box_push1 = p1, None
            np2, box_push2 = p2, None
            
        # 2. Cùng lao vào 1 ô
        if np1 == np2 and np1 != p1:
            np1, box_push1 = p1, None
            np2, box_push2 = p2, None
            
        # 3. Hai người cùng đẩy 1 hộp, hoặc đẩy 2 hộp vào cùng 1 ô
        if box_push1 and box_push2:
            if box_push1[0] == box_push2[0] or box_push1[1] == box_push2[1]:
                np1, box_push1 = p1, None
                np2, box_push2 = p2, None
                
        # 4. Agent lao vào hộp đang bị Agent kia đẩy (hoặc lao vào vị trí mới của Agent kia)
        if box_push1 and np2 == box_push1[0]:
            # P2 đi vào chỗ hộp mà P1 đẩy. Điều này hợp lệ nếu P1 đẩy thành công.
            pass
            
        # Cập nhật box
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

        # Thực thi đẩy hộp (chỉ ghi nhận cho người đẩy cuối cùng)
        if box_push1:
            update_box(box_push1[0], box_push1[1], 1)
        if box_push2:
            update_box(box_push2[0], box_push2[1], 2)
            
        return CompetitiveState(np1, np2, neutral_boxes, agent1_boxes, agent2_boxes)
