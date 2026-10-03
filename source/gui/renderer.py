import pygame

COLOR_BG       = (245, 245, 220)
COLOR_WALL     = (80,  80,  80)
COLOR_FLOOR    = (220, 210, 185)
COLOR_TARGET   = (220,  60,  60)
COLOR_BOX      = (200, 130,  50)
COLOR_BOX_ON   = (100,  60,  20)
COLOR_PLAYER   = ( 50,  80, 200)
COLOR_WHITE    = (255, 255, 255)
COLOR_PANEL_BG = ( 15,  20,  45)
COLOR_PANEL_BDR= ( 65,  65, 130)
COLOR_YELLOW   = (255, 215,   0)
COLOR_GREEN    = ( 80, 220, 100)
COLOR_GRAY     = (140, 135, 185)
COLOR_RED      = (220,  60,  60)

PANEL_H = 105


class Renderer:
    def __init__(self, screen, board):
        self.screen = screen
        self.board  = board
        self.font_ui  = pygame.font.SysFont("arial", 22)
        self.font_big = pygame.font.SysFont("arial", 28, bold=True)

        sw, sh = screen.get_size()
        max_w = sw - 40
        max_h = sh - PANEL_H - 40

        if board.width > 0 and board.height > 0:
            self.cell_size = min(max_w // board.width, max_h // board.height, 64)
        else:
            self.cell_size = 48

        map_pixel_w = board.width  * self.cell_size
        map_pixel_h = board.height * self.cell_size
        self.offset_x = max(0, (sw - map_pixel_w) // 2)
        self.offset_y = PANEL_H + max(0, (sh - PANEL_H - map_pixel_h) // 2)

        import os
        assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')

        def load_img(subfolder, name):
            path = os.path.join(assets_dir, subfolder, name)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (self.cell_size, self.cell_size))
            return None

        self.img_wall   = load_img('tiles', 'wall.png')
        self.img_floor  = load_img('tiles', 'floor.png')
        self.img_goal   = load_img('tiles', 'goal.png')
        self.img_box    = load_img('tiles', 'box.png')
        self.img_box_on = load_img('tiles', 'box_on_goal.png')
        self.img_player = load_img('sprites', 'player.png')

        import os as _os
        bg_path = _os.path.join(assets_dir, 'backgrounds', 'bg_main.jpg')
        if _os.path.exists(bg_path):
            bg_img = pygame.image.load(bg_path).convert()
            self.img_bg = pygame.transform.scale(bg_img, (sw, sh))
        else:
            self.img_bg = None

    def _cell_rect(self, row, col):
        x = self.offset_x + col * self.cell_size
        y = self.offset_y + row * self.cell_size
        return pygame.Rect(x, y, self.cell_size, self.cell_size)

    def draw_static(self):
        if self.img_bg:
            self.screen.blit(self.img_bg, (0, 0))
        else:
            self.screen.fill(COLOR_BG)

        panel_rect = pygame.Rect(0, 0, self.screen.get_width(), PANEL_H)
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, panel_rect)

        for row in range(self.board.height):
            for col in range(self.board.width):
                pos  = (row, col)
                rect = self._cell_rect(row, col)

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
                elif self.board.is_goal(pos):
                    if self.img_goal:
                        self.screen.blit(self.img_goal, rect)
                    else:
                        cx, cy = rect.centerx, rect.centery
                        r = self.cell_size // 4
                        pygame.draw.line(self.screen, COLOR_TARGET, (cx-r, cy-r), (cx+r, cy+r), 3)
                        pygame.draw.line(self.screen, COLOR_TARGET, (cx+r, cy-r), (cx-r, cy+r), 3)

    def draw_state(self, state):
        for bpos in state.boxes:
            row, col = bpos
            rect    = self._cell_rect(row, col)
            on_goal = self.board.is_goal(bpos)
            img     = self.img_box_on if on_goal else self.img_box
            if img:
                self.screen.blit(img, rect)
            else:
                color = COLOR_BOX_ON if on_goal else COLOR_BOX
                inner = rect.inflate(-8, -8)
                pygame.draw.rect(self.screen, color, inner, border_radius=4)
                pygame.draw.rect(self.screen, (0, 0, 0), inner, 1, border_radius=4)

        row, col = state.agent_pos
        rect = self._cell_rect(row, col)
        if self.img_player:
            self.screen.blit(self.img_player, rect)
        else:
            cx, cy = rect.centerx, rect.centery
            r = self.cell_size // 2 - 6
            pygame.draw.circle(self.screen, COLOR_PLAYER, (cx, cy), r)
            pygame.draw.circle(self.screen, COLOR_WHITE,  (cx, cy), r, 2)

    def draw_panel(self, info):
        sw = self.screen.get_width()

        algo_str = info.get("algorithm", "?").upper()
        step     = info.get("step", 0)
        total    = info.get("total_steps", 0)
        cost     = info.get("cost", 0)
        expanded = info.get("expanded", 0)
        status   = info.get("status", "paused").upper()

        surf_algo = self.font_big.render(f"Algorithm: {algo_str}", True, COLOR_YELLOW)
        self.screen.blit(surf_algo, (20, 10))

        status_color = COLOR_GREEN if status == "PLAYING" else COLOR_RED
        if status == "SOLVED":
            status_color = COLOR_YELLOW
        surf_status = self.font_big.render(status, True, status_color)
        self.screen.blit(surf_status, (sw - surf_status.get_width() - 20, 10))

        info_str  = f"Step: {step} / {total}    |    Cost: {cost}    |    Nodes expanded: {expanded:,}"
        surf_info = self.font_ui.render(info_str, True, COLOR_WHITE)
        self.screen.blit(surf_info, (20, 45))

        pygame.draw.line(self.screen, COLOR_PANEL_BDR, (20, 75), (sw - 20, 75))

        hint_str  = "Space: Play/Pause  |  <- ->: Step  |  Shift+<->: First/Last  |  Home/End  |  Esc: Menu"
        surf_hint = pygame.font.SysFont("arial", 18).render(hint_str, True, COLOR_GRAY)
        self.screen.blit(surf_hint, ((sw - surf_hint.get_width()) // 2, 82))

    def draw_message(self, text, color=COLOR_WHITE):
        sw, sh = self.screen.get_size()
        surf   = self.font_big.render(text, True, color)
        x = (sw - surf.get_width())  // 2
        y = (sh - surf.get_height()) // 2
        bg_rect = surf.get_rect(center=(sw//2, sh//2)).inflate(30, 20)
        bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 160))
        self.screen.blit(bg_surf, bg_rect.topleft)
        self.screen.blit(surf, (x, y))
