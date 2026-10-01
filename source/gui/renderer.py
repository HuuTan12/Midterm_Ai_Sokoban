import pygame

# ===== Màu sắc =====
COLOR_BG        = (245, 245, 220)   # Nền kem
COLOR_WALL      = (80,  80,  80)    # Tường xám đậm
COLOR_FLOOR     = (220, 210, 185)   # Ô đi được
COLOR_TARGET    = (220,  60,  60)   # Đích đỏ
COLOR_BOX       = (200, 130,  50)   # Hộp chưa vào đích (nâu)
COLOR_BOX_ON    = (100,  60,  20)   # Hộp đã vào đích (nâu đậm)
COLOR_PLAYER    = ( 50,  80, 200)   # Người chơi xanh dương
COLOR_WHITE     = (255, 255, 255)

# ── Tone màu panel HUD (đồng bộ với menu navy/tím) ──
COLOR_PANEL_BG  = ( 15,  20,  45)   # Nền HUD: navy đậm
COLOR_PANEL_BDR = ( 65,  65, 130)   # Viền HUD
COLOR_YELLOW    = (255, 215,   0)   # Vàng gold (tiêu đề, thông số)
COLOR_GREEN     = ( 80, 220, 100)   # Xanh lá (PLAYING)
COLOR_GRAY      = (140, 135, 185)   # Tím nhạt (ghi chú)
COLOR_RED       = (220,  60,  60)   # Đỏ (PAUSED / lỗi)
COLOR_CYAN      = (100, 210, 255)   # Xanh nhạt (SOLVED)
COLOR_HINT_KEY  = (220, 180, 255)   # Tím nhạt sáng (tên phím)
COLOR_HINT_TXT  = ( 90,  90, 145)   # Xám tím (phân cách |)

CELL_SIZE = 48   # Kích thước mỗi ô (pixel)
PANEL_H   = 105  # Chiều cao panel HUD (tăng để chứa 3 dòng + ghi chú)


class Renderer:
    """
    Lớp Renderer: chịu trách nhiệm vẽ toàn bộ game lên màn hình.
    Tách rời việc vẽ ra khỏi logic thuật toán (đúng nguyên tắc OOP).

    Hệ tọa độ nội bộ: (row, col) theo chuẩn của core/.
      - screen_x = PANEL_OFFSET_X + col * CELL_SIZE
      - screen_y = PANEL_H + row * CELL_SIZE
    """

    def __init__(self, screen, board):
        """
        screen : pygame.Surface (cửa sổ game)
        board  : core.board.Board (chứa walls, goals, width, height)
        """
        self.screen = screen
        self.board  = board
        self.font_ui    = pygame.font.SysFont("arial", 22)
        self.font_big   = pygame.font.SysFont("arial", 28, bold=True)

        # Tự động căn giữa map trên màn hình
        sw, sh = screen.get_size()
        map_pixel_w = board.width  * CELL_SIZE
        map_pixel_h = board.height * CELL_SIZE
        self.offset_x = max(0, (sw - map_pixel_w) // 2)
        self.offset_y = PANEL_H + max(0, (sh - PANEL_H - map_pixel_h) // 2)

        # Load assets
        import os
        assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
        
        def load_img(name):
            path = os.path.join(assets_dir, name)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
            return None

        self.img_wall = load_img('wall.png')
        self.img_floor = load_img('floor.png')
        self.img_goal = load_img('goal.png')
        self.img_box = load_img('box.png')
        self.img_box_on = load_img('box_on_goal.png')
        self.img_player = load_img('player.png')

    def _cell_rect(self, row, col):
        """Trả về pygame.Rect cho ô (row, col)."""
        x = self.offset_x + col * CELL_SIZE
        y = self.offset_y + row * CELL_SIZE
        return pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

    def draw_static(self):
        """Vẽ nền, tường và ô đích — những thứ không thay đổi theo bước."""
        self.screen.fill(COLOR_BG)

        # Vẽ nền panel HUD
        panel_rect = pygame.Rect(0, 0, self.screen.get_width(), PANEL_H)
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, panel_rect)

        # Vẽ từng ô trong map
        for row in range(self.board.height):
            for col in range(self.board.width):
                pos = (row, col)
                rect = self._cell_rect(row, col)
                
                # Luôn vẽ sàn bên dưới mọi thứ
                if self.img_floor:
                    self.screen.blit(self.img_floor, rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_FLOOR, rect)
                    pygame.draw.rect(self.screen, (200, 195, 175), rect, 1)

                if self.board.is_wall(pos):
                    if self.img_wall:
                        self.screen.blit(self.img_wall, rect)
                    else:
                        pygame.draw.rect(self.screen, COLOR_WALL, rect)
                        pygame.draw.rect(self.screen, (120, 120, 120), rect, 1)
                else:
                    # Vẽ điểm đích
                    if self.board.is_goal(pos):
                        if self.img_goal:
                            self.screen.blit(self.img_goal, rect)
                        else:
                            cx, cy = rect.centerx, rect.centery
                            r  = CELL_SIZE // 4
                            pygame.draw.line(self.screen, COLOR_TARGET, (cx-r, cy-r), (cx+r, cy+r), 3)
                            pygame.draw.line(self.screen, COLOR_TARGET, (cx+r, cy-r), (cx-r, cy+r), 3)

    def draw_state(self, state):
        """
        Vẽ trạng thái động: boxes và player.
        state : core.state.State  (agent_pos=(row,col), boxes=[(row,col),...])
        """
        # Vẽ boxes
        for bpos in state.boxes:
            row, col = bpos
            rect = self._cell_rect(row, col)
            on_goal = self.board.is_goal(bpos)
            
            img = self.img_box_on if on_goal else self.img_box
            if img:
                self.screen.blit(img, rect)
            else:
                color = COLOR_BOX_ON if on_goal else COLOR_BOX
                inner = rect.inflate(-8, -8)
                pygame.draw.rect(self.screen, color, inner, border_radius=4)
                pygame.draw.rect(self.screen, (0, 0, 0), inner, 1, border_radius=4)

        # Vẽ player
        row, col = state.agent_pos
        rect = self._cell_rect(row, col)
        
        if self.img_player:
            self.screen.blit(self.img_player, rect)
        else:
            cx, cy = rect.centerx, rect.centery
            r  = CELL_SIZE // 2 - 6
            pygame.draw.circle(self.screen, COLOR_PLAYER, (cx, cy), r)
            pygame.draw.circle(self.screen, COLOR_WHITE,  (cx, cy), r, 2)

    def draw_panel(self, info):
        """
        Vẽ HUD (panel thông tin phía trên).
        info : dict với các key:
            algorithm   : str  ("ucs" / "astar")
            step        : int  (bước hiện tại)
            total_steps : int  (tổng số bước)
            cost        : int  (chi phí)
            status      : str  ("playing" / "paused" / "solved")
        """
        sw = self.screen.get_width()

        algo_str  = info.get("algorithm", "?").upper()
        step      = info.get("step", 0)
        total     = info.get("total_steps", 0)
        cost      = info.get("cost", 0)
        status    = info.get("status", "paused").upper()

        # Dòng 1: tên thuật toán + số bước
        line1 = f"Thuat toan: {algo_str}   |   Buoc: {step} / {total}   |   Chi phi: {cost}"
        surf1 = self.font_big.render(line1, True, COLOR_YELLOW)
        self.screen.blit(surf1, (20, 10))

        # Dòng 2: hướng dẫn phím
        line2 = "Space: Play/Pause   |   <-  ->: Lui/Tien buoc   |   Esc: Quay lai menu"
        surf2 = self.font_ui.render(line2, True, COLOR_GRAY)
        self.screen.blit(surf2, (20, 46))

        # Trạng thái play/pause (góc phải)
        status_color = COLOR_GREEN if status == "PLAYING" else COLOR_RED
        if status == "SOLVED":
            status_color = COLOR_YELLOW
        surf_status = self.font_big.render(status, True, status_color)
        self.screen.blit(surf_status, (sw - surf_status.get_width() - 20, 25))

    def draw_message(self, text, color=COLOR_WHITE):
        """Vẽ một thông báo lớn ở giữa màn hình (dùng cho 'Đang tính...', 'Không có nghiệm')."""
        sw, sh = self.screen.get_size()
        surf = self.font_big.render(text, True, color)
        x = (sw - surf.get_width())  // 2
        y = (sh - surf.get_height()) // 2
        # Nền mờ phía sau chữ
        bg_rect = surf.get_rect(center=(sw//2, sh//2)).inflate(30, 20)
        bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 160))
        self.screen.blit(bg_surf, bg_rect.topleft)
        self.screen.blit(surf, (x, y))
