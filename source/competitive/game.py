import pygame
import time

WALL_COLOR          = (105, 105, 105)
BG_COLOR            = (240, 240, 240)
TARGET_COLOR        = (255,  50,  50)
PLAYER1_COLOR       = ( 50,  50, 255)
BOX1_COLOR          = (100, 100, 255)
BOX1_ON_TARGET_COLOR= (  0,   0, 150)
PLAYER2_COLOR       = ( 50, 255,  50)
BOX2_COLOR          = (100, 255, 100)
BOX2_ON_TARGET_COLOR= (  0, 150,   0)
NEUTRAL_BOX_COLOR   = (205, 133,  63)
CELL_SIZE           = 40


class CompetitiveGameScreen:
    def __init__(self, screen, map_path, actions1, actions2):
        self.screen   = screen
        self.map_path = map_path
        self.actions1 = actions1
        self.actions2 = actions2

        self.walls, self.targets, self.states = self._build_display_data(actions1, actions2)

        self.current_step    = 0
        self.is_playing      = False
        self.last_update_time= time.time()
        self.play_speed      = 0.3

        self.font = pygame.font.SysFont("arial", 30)

    def _build_display_data(self, actions1, actions2):
        import os, sys
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        src  = os.path.join(root, 'source')
        for p in [root, src]:
            if p not in sys.path:
                sys.path.insert(0, p)

        from source.core.map_parser import MapParser
        from source.core.competitive_rules import CompetitiveRules

        map_lines  = MapParser.load_map(self.map_path)
        board, comp_state = MapParser.parse_competitive_level(map_lines)

        walls   = {(c, r) for (r, c) in board.walls}
        targets = {(c, r) for (r, c) in board.goals}

        def to_display(s):
            b_dict = {}
            for (r, c) in s.neutral_boxes: b_dict[(c, r)] = 0
            for (r, c) in s.agent1_boxes:  b_dict[(c, r)] = 1
            for (r, c) in s.agent2_boxes:  b_dict[(c, r)] = 2
            p1 = (comp_state.agent1_pos[1], comp_state.agent1_pos[0]) \
                 if s.agent1_pos is None else (s.agent1_pos[1], s.agent1_pos[0])
            p2 = (comp_state.agent2_pos[1], comp_state.agent2_pos[0]) \
                 if s.agent2_pos is None else (s.agent2_pos[1], s.agent2_pos[0])
            return p1, p2, b_dict

        states    = [to_display(comp_state)]
        max_steps = max(len(actions1), len(actions2)) if (actions1 or actions2) else 0
        for i in range(max_steps):
            a1 = actions1[i] if i < len(actions1) else None
            a2 = actions2[i] if i < len(actions2) else None
            comp_state = CompetitiveRules.apply_actions(comp_state, a1, a2, board)
            states.append(to_display(comp_state))

        return walls, targets, states

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "BACK_TO_MENU"
            elif event.key == pygame.K_SPACE:
                self.is_playing = not self.is_playing
            elif event.key == pygame.K_RIGHT:
                self.is_playing = False
                if event.mod & pygame.KMOD_SHIFT:
                    self.current_step = len(self.states) - 1
                elif self.current_step < len(self.states) - 1:
                    self.current_step += 1
            elif event.key == pygame.K_LEFT:
                self.is_playing = False
                if event.mod & pygame.KMOD_SHIFT:
                    self.current_step = 0
                elif self.current_step > 0:
                    self.current_step -= 1
            elif event.key == pygame.K_HOME:
                self.is_playing   = False
                self.current_step = 0
            elif event.key == pygame.K_END:
                self.is_playing   = False
                self.current_step = len(self.states) - 1
        return None

    def update(self):
        if self.is_playing:
            now = time.time()
            if now - self.last_update_time > self.play_speed:
                if self.current_step < len(self.states) - 1:
                    self.current_step     += 1
                    self.last_update_time  = now
                else:
                    self.is_playing = False

    def draw(self):
        if self.walls:
            max_wx = max(x for x, y in self.walls)
            max_wy = max(y for x, y in self.walls)
        else:
            max_wx, max_wy = 10, 10

        sw, sh  = self.screen.get_size()
        PANEL_H = 105

        if not hasattr(self, 'cell_size'):
            max_w = sw - 40
            max_h = sh - PANEL_H - 40
            self.cell_size = min(max_w // (max_wx + 1), max_h // (max_wy + 1), 64)
            if self.cell_size <= 0:
                self.cell_size = 48

        map_pixel_w = (max_wx + 1) * self.cell_size
        map_pixel_h = (max_wy + 1) * self.cell_size
        offset_x    = max(0, (sw - map_pixel_w) // 2)
        offset_y    = PANEL_H + max(0, (sh - PANEL_H - map_pixel_h) // 2)

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
                bg_img  = pygame.image.load(bg_path).convert()
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
                rect = (offset_x + gx * self.cell_size, offset_y + gy * self.cell_size,
                        self.cell_size, self.cell_size)
                if self.img_floor:
                    self.screen.blit(self.img_floor, rect)
                else:
                    pygame.draw.rect(self.screen, BG_COLOR, rect)

        for wx, wy in self.walls:
            rect = (offset_x + wx * self.cell_size, offset_y + wy * self.cell_size,
                    self.cell_size, self.cell_size)
            if self.img_wall:
                self.screen.blit(self.img_wall, rect)
            else:
                pygame.draw.rect(self.screen, WALL_COLOR, rect)

        for tx, ty in self.targets:
            rect = (offset_x + tx * self.cell_size, offset_y + ty * self.cell_size,
                    self.cell_size, self.cell_size)
            if self.img_goal:
                self.screen.blit(self.img_goal, rect)
            else:
                pygame.draw.circle(self.screen, TARGET_COLOR,
                                   (offset_x + tx * self.cell_size + self.cell_size // 2,
                                    offset_y + ty * self.cell_size + self.cell_size // 2),
                                   self.cell_size // 4)

        for (bx, by), owner in boxes_dict.items():
            rect      = (offset_x + bx * self.cell_size, offset_y + by * self.cell_size,
                         self.cell_size, self.cell_size)
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

        px, py = p1_pos
        rect1  = (offset_x + px * self.cell_size, offset_y + py * self.cell_size,
                  self.cell_size, self.cell_size)
        if self.img_player1:
            self.screen.blit(self.img_player1, rect1)
        else:
            pygame.draw.circle(self.screen, PLAYER1_COLOR,
                               (offset_x + px * self.cell_size + self.cell_size // 2,
                                offset_y + py * self.cell_size + self.cell_size // 2),
                               self.cell_size // 2 - 4)

        px2, py2 = p2_pos
        rect2    = (offset_x + px2 * self.cell_size, offset_y + py2 * self.cell_size,
                    self.cell_size, self.cell_size)
        if self.img_player2:
            self.screen.blit(self.img_player2, rect2)
        else:
            pygame.draw.circle(self.screen, PLAYER2_COLOR,
                               (offset_x + px2 * self.cell_size + self.cell_size // 2,
                                offset_y + py2 * self.cell_size + self.cell_size // 2),
                               self.cell_size // 2 - 4)

        PANEL_H    = 105
        sw         = self.screen.get_width()
        panel_rect = pygame.Rect(0, 0, sw, PANEL_H)
        pygame.draw.rect(self.screen, (15, 20, 45), panel_rect)

        total_steps = len(self.states) - 1
        is_ended    = (self.current_step >= total_steps)
        status_text = "SOLVED" if is_ended else ("PLAYING" if self.is_playing else "PAUSED")

        score1 = sum(1 for (bx, by), owner in boxes_dict.items() if owner == 1 and (bx, by) in self.targets)
        score2 = sum(1 for (bx, by), owner in boxes_dict.items() if owner == 2 and (bx, by) in self.targets)

        winner_text = ""
        if is_ended:
            if score1 > score2:   winner_text = " - AGENT 1 WINS!"
            elif score2 > score1: winner_text = " - AGENT 2 WINS!"
            else:                 winner_text = " - DRAW!"

        f_title    = pygame.font.SysFont("arial", 28, bold=True)
        title_str  = "COMPETITIVE MODE (A* vs UCS)" + winner_text
        surf_title = f_title.render(title_str, True, (255, 215, 0))
        self.screen.blit(surf_title, (20, 10))

        c_status    = (80, 220, 100) if status_text == "PLAYING" else ((255, 215, 0) if status_text == "SOLVED" else (220, 60, 60))
        surf_status = f_title.render(status_text, True, c_status)
        self.screen.blit(surf_status, (sw - surf_status.get_width() - 20, 10))

        f_info      = pygame.font.SysFont("arial", 22)
        info_part   = f_info.render(f"Step: {self.current_step} / {total_steps}    |    ", True, (255, 255, 255))
        self.screen.blit(info_part, (20, 45))
        cx = 20 + info_part.get_width()

        s1_surf = f_info.render(f"A1 (Tan): {score1} pts", True, (100, 150, 255))
        self.screen.blit(s1_surf, (cx, 45))
        cx += s1_surf.get_width()

        sep_surf = f_info.render("   -   ", True, (255, 255, 255))
        self.screen.blit(sep_surf, (cx, 45))
        cx += sep_surf.get_width()

        s2_surf = f_info.render(f"A2 (Hieu): {score2} pts", True, (100, 255, 100))
        self.screen.blit(s2_surf, (cx, 45))

        pygame.draw.line(self.screen, (65, 65, 130), (20, 75), (sw - 20, 75))

        hint_str  = "Space: Play/Pause  |  <- ->: Step  |  Shift+<->: First/Last  |  Home/End  |  Esc: Menu"
        surf_hint = pygame.font.SysFont("arial", 18).render(hint_str, True, (140, 135, 185))
        self.screen.blit(surf_hint, ((sw - surf_hint.get_width()) // 2, 82))

        if is_ended:
            font_huge = pygame.font.SysFont("arial", 50, bold=True)
            msg       = winner_text.replace(" - ", "")
            c_win     = (100, 150, 255) if score1 > score2 else ((255, 100, 100) if score2 > score1 else (255, 215, 0))
            text_surf = font_huge.render(msg, True, c_win)

            sh_local  = self.screen.get_height()
            overlay   = pygame.Surface((sw, sh_local), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))

            tx = (sw - text_surf.get_width())  // 2
            ty = (sh_local - text_surf.get_height()) // 2
            outline   = font_huge.render(msg, True, (0, 0, 0))
            for dx, dy in [(-2,-2), (2,-2), (-2,2), (2,2)]:
                self.screen.blit(outline, (tx + dx, ty + dy))
            self.screen.blit(text_surf, (tx, ty))

            font_small = pygame.font.SysFont("arial", 24)
            esc_surf   = font_small.render("Press ESC to return to Menu", True, (200, 200, 200))
            self.screen.blit(esc_surf, ((sw - esc_surf.get_width()) // 2, ty + 70))