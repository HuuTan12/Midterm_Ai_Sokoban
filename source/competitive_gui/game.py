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

CELL_SIZE = 40


class CompetitiveGameScreen:
    def __init__(self, screen, map_path, actions1, actions2):
        self.screen = screen
        self.map_path = map_path
        self.actions1 = actions1
        self.actions2 = actions2

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
        """Xử lý phím Space, Left, Right, Home, End, Shift+Left/Right và Escape."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "BACK_TO_MENU"
            elif event.key == pygame.K_SPACE:
                self.is_playing = not self.is_playing
            elif event.key == pygame.K_RIGHT:
                self.is_playing = False
                if event.mod & pygame.KMOD_SHIFT:
                    # Shift+Phải → nhảy đến bước cuối
                    self.current_step = len(self.states) - 1
                elif self.current_step < len(self.states) - 1:
                    self.current_step += 1
            elif event.key == pygame.K_LEFT:
                self.is_playing = False
                if event.mod & pygame.KMOD_SHIFT:
                    # Shift+Trái → nhảy về bước đầu
                    self.current_step = 0
                elif self.current_step > 0:
                    self.current_step -= 1
            elif event.key == pygame.K_HOME:
                self.is_playing = False
                self.current_step = 0
            elif event.key == pygame.K_END:
                self.is_playing = False
                self.current_step = len(self.states) - 1
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
        # Tìm kích thước map để căn giữa và tính cell_size
        if self.walls:
            max_wx = max(x for x, y in self.walls)
            max_wy = max(y for x, y in self.walls)
        else:
            max_wx, max_wy = 10, 10
            
        sw, sh = self.screen.get_size()
        PANEL_H = 105
        
        if not hasattr(self, 'cell_size'):
            max_w = sw - 40
            max_h = sh - PANEL_H - 40
            self.cell_size = min(max_w // (max_wx + 1), max_h // (max_wy + 1), 64)
            if self.cell_size <= 0:
                self.cell_size = 48

        # Căn giữa map
        map_pixel_w = (max_wx + 1) * self.cell_size
        map_pixel_h = (max_wy + 1) * self.cell_size
        offset_x = max(0, (sw - map_pixel_w) // 2)
        offset_y = PANEL_H + max(0, (sh - PANEL_H - map_pixel_h) // 2)

        # Load assets dynamically on first draw if not loaded
        if not hasattr(self, 'img_wall'):
            import os
            assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')

            def load_img(subfolder, name):
                path = os.path.join(assets_dir, subfolder, name)
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    return pygame.transform.scale(img, (self.cell_size, self.cell_size))
                return None

            self.img_wall        = load_img('tiles', 'wall.png')
            self.img_floor       = load_img('tiles', 'floor.png')
            self.img_goal        = load_img('tiles', 'goal.png')
            self.img_box1        = load_img('tiles', 'box.png')
            self.img_box1_on     = load_img('tiles', 'box_on_goal.png')
            self.img_box2        = load_img('tiles', 'box2.png')
            self.img_box2_on     = load_img('tiles', 'box2_on_goal.png')
            self.img_box_neutral = load_img('tiles', 'box.png')
            self.img_player1     = load_img('sprites', 'player.png')
            self.img_player2     = load_img('sprites', 'player2.png')
            
            bg_path = os.path.join(assets_dir, 'backgrounds', 'bg_main.jpg')
            if os.path.exists(bg_path):
                bg_img = pygame.image.load(bg_path).convert()
                self.img_bg = pygame.transform.scale(bg_img, self.screen.get_size())
            else:
                self.img_bg = None

        if hasattr(self, 'img_bg') and self.img_bg:
            self.screen.blit(self.img_bg, (0, 0))
        else:
            self.screen.fill(BG_COLOR)

        p1_pos, p2_pos, boxes_dict = self.states[self.current_step]
        for gy in range(max_wy + 1):
            for gx in range(max_wx + 1):
                rect = (offset_x + gx * self.cell_size, offset_y + gy * self.cell_size, self.cell_size, self.cell_size)
                if self.img_floor:
                    self.screen.blit(self.img_floor, rect)
                else:
                    pygame.draw.rect(self.screen, BG_COLOR, rect)

        # Vẽ tường
        for wx, wy in self.walls:
            rect = (offset_x + wx * self.cell_size, offset_y + wy * self.cell_size, self.cell_size, self.cell_size)
            if self.img_wall:
                self.screen.blit(self.img_wall, rect)
            else:
                pygame.draw.rect(self.screen, WALL_COLOR, rect)

        # Vẽ điểm đích
        for tx, ty in self.targets:
            rect = (offset_x + tx * self.cell_size, offset_y + ty * self.cell_size, self.cell_size, self.cell_size)
            if self.img_goal:
                self.screen.blit(self.img_goal, rect)
            else:
                pygame.draw.circle(self.screen, TARGET_COLOR,
                                   (offset_x + tx * self.cell_size + self.cell_size // 2,
                                    offset_y + ty * self.cell_size + self.cell_size // 2),
                                   self.cell_size // 4)

        # Vẽ boxes
        for (bx, by), owner in boxes_dict.items():
            rect = (offset_x + bx * self.cell_size, offset_y + by * self.cell_size, self.cell_size, self.cell_size)
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
                inner = (offset_x + bx * self.cell_size + 2, offset_y + by * self.cell_size + 2,
                         self.cell_size - 4, self.cell_size - 4)
                pygame.draw.rect(self.screen, color, inner)

        # Vẽ người chơi 1
        px, py = p1_pos
        rect1 = (offset_x + px * self.cell_size, offset_y + py * self.cell_size, self.cell_size, self.cell_size)
        if self.img_player1:
            self.screen.blit(self.img_player1, rect1)
        else:
            pygame.draw.circle(self.screen, PLAYER1_COLOR,
                               (offset_x + px * self.cell_size + self.cell_size // 2,
                                offset_y + py * self.cell_size + self.cell_size // 2),
                               self.cell_size // 2 - 4)

        # Vẽ người chơi 2
        px2, py2 = p2_pos
        rect2 = (offset_x + px2 * self.cell_size, offset_y + py2 * self.cell_size, self.cell_size, self.cell_size)
        if self.img_player2:
            self.screen.blit(self.img_player2, rect2)
        else:
            pygame.draw.circle(self.screen, PLAYER2_COLOR,
                               (offset_x + px2 * self.cell_size + self.cell_size // 2,
                                offset_y + py2 * self.cell_size + self.cell_size // 2),
                               self.cell_size // 2 - 4)

        # ── Vẽ HUD panel (Đồng bộ với Single Player) ──
        PANEL_H = 105
        sw = self.screen.get_width()
        panel_rect = pygame.Rect(0, 0, sw, PANEL_H)
        pygame.draw.rect(self.screen, (15, 20, 45), panel_rect)    # COLOR_PANEL_BG
        pygame.draw.line(self.screen, (65, 65, 130), (0, PANEL_H - 1), (sw, PANEL_H - 1), 2)  # COLOR_PANEL_BDR

        total_steps = len(self.states) - 1
        is_ended = (self.current_step >= total_steps)
        status_text = "SOLVED" if is_ended else ("PLAYING" if self.is_playing else "PAUSED")

        # Tính điểm hiện tại
        score1 = sum(1 for (bx, by), owner in boxes_dict.items() if owner == 1 and (bx, by) in self.targets)
        score2 = sum(1 for (bx, by), owner in boxes_dict.items() if owner == 2 and (bx, by) in self.targets)

        # Thông báo kết quả nếu kết thúc
        winner_text = ""
        if is_ended:
            if score1 > score2:
                winner_text = " - AGENT 1 WINS!"
            elif score2 > score1:
                winner_text = " - AGENT 2 WINS!"
            else:
                winner_text = " - DRAW!"

        # Dòng 1
        line1 = f"COMPETITIVE (A* vs UCS)   |   Step: {self.current_step} / {total_steps}   |   Score: A1({score1}) - A2({score2}){winner_text}"
        surf1 = self.font.render(line1, True, (255, 215, 0))
        self.screen.blit(surf1, (20, 15))

        # Dòng phân cách mờ
        pygame.draw.line(self.screen, (45, 50, 80), (20, 52), (sw - 20, 52))

        # Dòng 2: Hướng dẫn
        f_ui = pygame.font.SysFont("arial", 18, bold=True)
        hints = [
            ("Space", "Play/Pause"), ("|", ""),
            ("<- ->", "Lui/Tien buoc"), ("|", ""),
            ("Shift+<->", "Dau/Cuoi"), ("|", ""),
            ("Home/End", "Dau/Cuoi"), ("|", ""),
            ("Esc", "Quay lai Menu")
        ]
        x_offset, y_hint = 20, 62
        for key, text in hints:
            if key == "|":
                surf = f_ui.render("   |   ", True, (90, 90, 145))
                self.screen.blit(surf, (x_offset, y_hint))
                x_offset += surf.get_width()
            else:
                key_surf = f_ui.render(key + ": ", True, (220, 180, 255))
                txt_surf = f_ui.render(text, True, (140, 135, 185))
                self.screen.blit(key_surf, (x_offset, y_hint))
                x_offset += key_surf.get_width()
                self.screen.blit(txt_surf, (x_offset, y_hint))
                x_offset += txt_surf.get_width()

        # Trạng thái (góc phải)
        c_status = (80, 220, 100) if status_text == "PLAYING" else ((100, 210, 255) if status_text == "SOLVED" else (220, 60, 60))
        surf_status = self.font.render(status_text, True, c_status)
        self.screen.blit(surf_status, (sw - surf_status.get_width() - 20, 15))

        # Hiển thị thông báo lớn giữa màn hình khi kết thúc
        if is_ended:
            font_huge = pygame.font.SysFont("arial", 50, bold=True)
            msg = winner_text.replace(" - ", "")
            
            # Chọn màu theo người thắng
            if score1 > score2:
                c_win = (100, 150, 255)  # Màu Agent 1 (Xanh dương)
            elif score2 > score1:
                c_win = (255, 100, 100)  # Màu Agent 2 (Đỏ)
            else:
                c_win = (255, 215, 0)    # Hòa (Vàng)

            text_surf = font_huge.render(msg, True, c_win)
            
            # Vẽ nền đen mờ
            sh = self.screen.get_height()
            overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))

            # Vẽ chữ có viền (outline)
            tx = (sw - text_surf.get_width()) // 2
            ty = (sh - text_surf.get_height()) // 2
            
            outline_surf = font_huge.render(msg, True, (0, 0, 0))
            for dx, dy in [(-2,-2), (2,-2), (-2,2), (2,2)]:
                self.screen.blit(outline_surf, (tx + dx, ty + dy))
            
            self.screen.blit(text_surf, (tx, ty))

            # Hướng dẫn thoát
            font_small = pygame.font.SysFont("arial", 24)
            esc_surf = font_small.render("Press ESC to return to Menu", True, (200, 200, 200))
            self.screen.blit(esc_surf, ((sw - esc_surf.get_width()) // 2, ty + 70))