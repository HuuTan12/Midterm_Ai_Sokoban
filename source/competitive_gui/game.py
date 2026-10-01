import pygame
import time

# Colors
WALL_COLOR = (105, 105, 105)       # Xám (%)
BG_COLOR = (240, 240, 240)         # Nền
TARGET_COLOR = (255, 50, 50)       # Đỏ (D)

# Colors for Agent 1
PLAYER1_COLOR = (50, 50, 255)       # Xanh dương
BOX1_COLOR = (100, 100, 255)        # Hộp của P1 chưa vào đích
BOX1_ON_TARGET_COLOR = (0, 0, 150)  # Hộp của P1 đã vào đích

# Colors for Agent 2
PLAYER2_COLOR = (50, 255, 50)       # Xanh lá
BOX2_COLOR = (100, 255, 100)        # Hộp của P2 chưa vào đích
BOX2_ON_TARGET_COLOR = (0, 150, 0)  # Hộp của P2 đã vào đích

NEUTRAL_BOX_COLOR = (205, 133, 63)  # Hộp trung lập

TEXT_COLOR = (0, 0, 0)

CELL_SIZE = 64


class CompetitiveGameScreen:
    def __init__(self, screen, map_path, actions1, actions2):
        self.screen = screen
        self.map_path = map_path
        self.actions1 = actions1
        self.actions2 = actions2

        import os
        assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
        
        def load_img(name):
            path = os.path.join(assets_dir, name)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
            return None

        # Tải hình ảnh để giao diện đẹp như 1 agent
        self.img_wall = load_img('wall.png')
        self.img_floor = load_img('floor.png')
        self.img_goal = load_img('goal.png')
        self.img_box1 = load_img('box.png')
        self.img_box1_on = load_img('box_on_goal.png')
        self.img_box2 = load_img('box2.png')
        self.img_box2_on = load_img('box2_on_goal.png')
        self.img_box_neutral = load_img('box.png')  # Dùng tạm box.png cho hộp trung lập
        self.img_player1 = load_img('player.png')
        self.img_player2 = load_img('player2.png')  # Đã đổi thành player2.png để phân biệt 2 agent

        # === FIX: Dùng DUY NHẤT MapParser để parse map, tránh 2 hệ tọa độ ===
        # generate_states sẽ build tất cả dữ liệu hiển thị từ CompetitiveState thật
        self.walls, self.targets, self.states = self._build_display_data(actions1, actions2)

        self.current_step = 0
        self.is_playing = False
        self.last_update_time = time.time()
        self.play_speed = 0.3  # Thời gian mỗi bước khi auto-play (giây)

        self.font = pygame.font.SysFont("arial", 30)

    def _build_display_data(self, actions1, actions2):
        """
        Parse map bằng MapParser (hệ row, col), chạy lại simulation để tạo
        danh sách trạng thái hiển thị dùng hệ (col, row) = (x, y) của pygame.
        Đây là cách DUY NHẤT tránh bị delay/lệch tọa độ giữa 2 agent.
        """
        import os, sys
        # Đảm bảo có thể import core
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        src  = os.path.join(root, 'source')
        for p in [root, src]:
            if p not in sys.path:
                sys.path.insert(0, p)

        from core.map_parser import MapParser
        from core.competitive_rules import CompetitiveRules

        map_lines = MapParser.load_map(self.map_path)
        board, comp_state = MapParser.parse_competitive_level(map_lines)

        # Chuyển walls và goals sang hệ (x, y) = (col, row) cho pygame
        walls   = {(c, r) for (r, c) in board.walls}
        targets = {(c, r) for (r, c) in board.goals}

        # Hàm chuyển CompetitiveState → tuple hiển thị trong hệ (x, y)
        def to_display(s):
            b_dict = {}
            for (r, c) in s.neutral_boxes:  b_dict[(c, r)] = 0
            for (r, c) in s.agent1_boxes:   b_dict[(c, r)] = 1
            for (r, c) in s.agent2_boxes:   b_dict[(c, r)] = 2

            # === FIX: Kiểm tra None trước khi unpack ===
            p1 = (comp_state.agent1_pos[1], comp_state.agent1_pos[0]) \
                 if s.agent1_pos is None else (s.agent1_pos[1], s.agent1_pos[0])
            p2 = (comp_state.agent2_pos[1], comp_state.agent2_pos[0]) \
                 if s.agent2_pos is None else (s.agent2_pos[1], s.agent2_pos[0])

            return p1, p2, b_dict

        states = [to_display(comp_state)]

        max_steps = max(len(actions1), len(actions2)) if (actions1 or actions2) else 0
        for i in range(max_steps):
            a1 = actions1[i] if i < len(actions1) else None
            a2 = actions2[i] if i < len(actions2) else None
            comp_state = CompetitiveRules.apply_actions(comp_state, a1, a2, board)
            states.append(to_display(comp_state))

        return walls, targets, states

    def handle_event(self, event):
        """Xử lý phím Space, Left, Right và Escape."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "BACK_TO_MENU"
            elif event.key == pygame.K_SPACE:
                self.is_playing = not self.is_playing
            elif event.key == pygame.K_RIGHT:
                self.is_playing = False
                if self.current_step < len(self.states) - 1:
                    self.current_step += 1
            elif event.key == pygame.K_LEFT:
                self.is_playing = False
                if self.current_step > 0:
                    self.current_step -= 1
        return None

    def update(self):
        """Cập nhật trạng thái nếu đang auto-play."""
        if self.is_playing:
            now = time.time()
            if now - self.last_update_time > self.play_speed:
                if self.current_step < len(self.states) - 1:
                    self.current_step += 1
                    self.last_update_time = now
                else:
                    self.is_playing = False

    def draw(self):
        self.screen.fill(BG_COLOR)

        p1_pos, p2_pos, boxes_dict = self.states[self.current_step]
        
        sw, sh = self.screen.get_size()
        max_wx = max([wx for wx, wy in self.walls]) if self.walls else 10
        max_wy = max([wy for wx, wy in self.walls]) if self.walls else 10
        map_w = (max_wx + 1) * CELL_SIZE
        map_h = (max_wy + 1) * CELL_SIZE
        offset_x = max(0, (sw - map_w) // 2)
        offset_y = 100 + max(0, (sh - 100 - map_h) // 2)
        
        # Vẽ sàn
        for wx in range(max_wx + 1):
            for wy in range(max_wy + 1):
                rect = (offset_x + wx * CELL_SIZE, offset_y + wy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if self.img_floor:
                    self.screen.blit(self.img_floor, rect)
                else:
                    pygame.draw.rect(self.screen, (220, 210, 185), rect)
                    pygame.draw.rect(self.screen, (200, 195, 175), rect, 1)

        # Vẽ tường
        for wx, wy in self.walls:
            rect = (offset_x + wx * CELL_SIZE, offset_y + wy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if self.img_wall:
                self.screen.blit(self.img_wall, rect)
            else:
                pygame.draw.rect(self.screen, WALL_COLOR, rect)
                pygame.draw.rect(self.screen, (120, 120, 120), rect, 1)

        # Vẽ điểm đích
        for tx, ty in self.targets:
            rect = (offset_x + tx * CELL_SIZE, offset_y + ty * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if self.img_goal:
                self.screen.blit(self.img_goal, rect)
            else:
                cx = offset_x + tx * CELL_SIZE + CELL_SIZE // 2
                cy = offset_y + ty * CELL_SIZE + CELL_SIZE // 2
                r = CELL_SIZE // 4
                pygame.draw.line(self.screen, TARGET_COLOR, (cx-r, cy-r), (cx+r, cy+r), 3)
                pygame.draw.line(self.screen, TARGET_COLOR, (cx+r, cy-r), (cx-r, cy+r), 3)

        # Vẽ boxes
        for (bx, by), owner in boxes_dict.items():
            rect = (offset_x + bx * CELL_SIZE, offset_y + by * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            on_target = (bx, by) in self.targets

            if owner == 1:
                img   = self.img_box1_on if on_target else self.img_box1
                color = BOX1_ON_TARGET_COLOR if on_target else BOX1_COLOR
            elif owner == 2:
                img   = self.img_box2_on if on_target else self.img_box2
                color = BOX2_ON_TARGET_COLOR if on_target else BOX2_COLOR
            else:
                img   = self.img_box_neutral
                color = NEUTRAL_BOX_COLOR

            if img:
                self.screen.blit(img, rect)
            else:
                inner = pygame.Rect(rect).inflate(-8, -8)
                pygame.draw.rect(self.screen, color, inner, border_radius=4)
                pygame.draw.rect(self.screen, (0, 0, 0), inner, 1, border_radius=4)

        # Vẽ người chơi 1
        px, py = p1_pos
        rect1 = (offset_x + px * CELL_SIZE, offset_y + py * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        if self.img_player1:
            self.screen.blit(self.img_player1, rect1)
        else:
            cx, cy = rect1[0] + CELL_SIZE // 2, rect1[1] + CELL_SIZE // 2
            r = CELL_SIZE // 2 - 6
            pygame.draw.circle(self.screen, PLAYER1_COLOR, (cx, cy), r)
            pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), r, 2)

        # Vẽ người chơi 2
        px2, py2 = p2_pos
        rect2 = (offset_x + px2 * CELL_SIZE, offset_y + py2 * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        if self.img_player2:
            self.screen.blit(self.img_player2, rect2)
        else:
            cx, cy = rect2[0] + CELL_SIZE // 2, rect2[1] + CELL_SIZE // 2
            r = CELL_SIZE // 2 - 6
            pygame.draw.circle(self.screen, PLAYER2_COLOR, (cx, cy), r)
            pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), r, 2)

        # UI thông tin
        total_steps = len(self.states) - 1
        
        # Calculate Scores
        score1 = sum(1 for (bx, by), owner in boxes_dict.items() if owner == 1 and (bx, by) in self.targets)
        score2 = sum(1 for (bx, by), owner in boxes_dict.items() if owner == 2 and (bx, by) in self.targets)
        
        # Win Declaration
        if self.current_step >= total_steps:
            if score1 > score2:
                status_text = "FINISHED - AGENT 1 (XANH DUONG) WINS!"
                status_color = (0, 0, 255)
            elif score2 > score1:
                status_text = "FINISHED - AGENT 2 (XANH LA) WINS!"
                status_color = (0, 150, 0)
            else:
                status_text = "FINISHED - TIE!"
                status_color = (200, 150, 0)
        else:
            status_text = "PLAYING" if self.is_playing else "PAUSED"
            status_color = TEXT_COLOR
            
        info_text = f"Step: {self.current_step} / {total_steps} | P1 Score: {score1} | P2 Score: {score2}"
        
        ui_surf1 = self.font.render(info_text, True, TEXT_COLOR)
        ui_surf2 = self.font.render(f"Trạng thái: {status_text} (Space: Play | Left/Right: Step | Esc: Menu)", True, status_color)
        
        self.screen.blit(ui_surf1, (20, 20))
        self.screen.blit(ui_surf2, (20, 60))