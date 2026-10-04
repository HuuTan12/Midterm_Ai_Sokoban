import pygame
import os

BG_TOP      = (15,  20,  45)
BG_BOT      = (30,  15,  60)
GOLD        = (255, 215,   0)
GOLD_DIM    = ( 80,  55,   0)
SUBTITLE    = (160, 155, 210)
HINT_COLOR  = ( 90,  90, 140)
PANEL_BG    = ( 25,  25,  55)
PANEL_BDR   = ( 65,  65, 130)
ROW_NORMAL  = ( 35,  35,  72)
ROW_SELECT  = ( 65,  40, 135)
ROW_BDR_N   = ( 60,  60, 120)
ROW_BDR_S   = (190, 145, 255)
ROW_TXT_N   = (175, 175, 215)
ROW_TXT_S   = (255, 255, 255)
ALGO_NORMAL = ( 40,  40,  85)
ALGO_SELECT = ( 90,  55, 170)
ALGO_BDR_N  = ( 70,  70, 140)
ALGO_BDR_S  = (220, 170, 255)
ALGO_TXT_N  = (160, 155, 210)
BTN_BG      = ( 50, 130,  70)
BTN_BDR     = (100, 220, 130)
BTN_TXT     = (220, 255, 230)
AGENT1_COL  = (100, 150, 255)
AGENT2_COL  = (100, 220, 130)
VS_COLOR    = (255, 180,  50)

ALGO_LIST = ["ucs", "astar"]
ALGO_INFO = {
    "ucs":   ("UCS",  "Uniform Cost Search",      "Search by increasing cost"),
    "astar": ("A*",   "A* (Hungarian-Chebyshev)",  "Optimal assignment + Deadlock handling"),
}


class MenuScreen:
    def __init__(self, screen, map_paths, is_competitive=False):
        self.screen         = screen
        self.map_paths      = map_paths
        self.is_competitive = is_competitive
        self.selected_map   = 0
        self.selected_algo  = 0
        self.algorithms     = ALGO_LIST
        self.is_confirmed   = False
        self.step_limit_str = ""

        self.font_title = pygame.font.SysFont("arial", 40, bold=True)
        self.font_sub   = pygame.font.SysFont("arial", 16)
        self.font_sec   = pygame.font.SysFont("arial", 14, bold=True)
        self.font_row   = pygame.font.SysFont("arial", 18, bold=True)
        self.font_algo  = pygame.font.SysFont("arial", 20, bold=True)
        self.font_small = pygame.font.SysFont("arial", 13)
        self.font_btn   = pygame.font.SysFont("arial", 19, bold=True)
        self.font_hint  = pygame.font.SysFont("arial", 13)

        sw, sh = screen.get_size()
        self.bg = pygame.Surface((sw, sh))
        for y in range(sh):
            t = y / sh
            r = int(BG_TOP[0] * (1 - t) + BG_BOT[0] * t)
            g = int(BG_TOP[1] * (1 - t) + BG_BOT[1] * t)
            b = int(BG_TOP[2] * (1 - t) + BG_BOT[2] * t)
            pygame.draw.line(self.bg, (r, g, b), (0, y), (sw, y))

        self.map_rects  = []
        self.algo_rects = []
        self.start_rect = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_map = (self.selected_map - 1) % max(len(self.map_paths), 1)
            elif event.key == pygame.K_DOWN:
                self.selected_map = (self.selected_map + 1) % max(len(self.map_paths), 1)
            elif event.key == pygame.K_LEFT and not self.is_competitive:
                self.selected_algo = (self.selected_algo - 1) % len(self.algorithms)
            elif event.key == pygame.K_RIGHT and not self.is_competitive:
                self.selected_algo = (self.selected_algo + 1) % len(self.algorithms)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.is_confirmed = True
                return True
            elif self.is_competitive:
                if event.key == pygame.K_BACKSPACE:
                    self.step_limit_str = self.step_limit_str[:-1]
                elif event.unicode.isdigit() and len(self.step_limit_str) < 3:
                    self.step_limit_str += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.map_rects):
                if rect.collidepoint(event.pos):
                    self.selected_map = i
            for i, rect in enumerate(self.algo_rects):
                if rect.collidepoint(event.pos):
                    self.selected_algo = i
            if self.start_rect and self.start_rect.collidepoint(event.pos):
                self.is_confirmed = True
                return True

        elif event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self.map_rects):
                if rect.collidepoint(event.pos):
                    self.selected_map = i

        return False

    def draw(self):
        sw, sh = self.screen.get_size()
        self.screen.blit(self.bg, (0, 0))

        title = "CHOOSE MAP  -  COMPETITIVE" if self.is_competitive else "CHOOSE MAP & ALGORITHM"
        shadow = self.font_title.render(title, True, GOLD_DIM)
        text   = self.font_title.render(title, True, GOLD)
        tx = (sw - text.get_width()) // 2
        ty = 24
        self.screen.blit(shadow, (tx + 3, ty + 3))
        self.screen.blit(text,   (tx,     ty))

        line_y = ty + text.get_height() + 4
        pygame.draw.line(self.screen, GOLD, (tx, line_y), (tx + text.get_width(), line_y), 2)

        if self.is_competitive:
            sub_txt = "Up/Down: select Map   |   Type numbers: set Max Steps   |   Enter / Click: Start"
        else:
            sub_txt = "Up/Down: select Map   |   Left/Right: select Algorithm   |   Enter / Click: Confirm"
        sub = self.font_sub.render(sub_txt, True, SUBTITLE)
        self.screen.blit(sub, ((sw - sub.get_width()) // 2, line_y + 5))

        PADDING   = 20
        COL_GAP   = 16
        CONTENT_Y = line_y + 38
        BOTTOM_Y  = sh - 70

        col_w   = (sw - PADDING * 2 - COL_GAP) // 2
        left_x  = PADDING
        right_x = PADDING + col_w + COL_GAP
        panel_h = BOTTOM_Y - CONTENT_Y

        self._draw_map_panel(left_x, CONTENT_Y, col_w, panel_h)

        if self.is_competitive:
            self._draw_competitive_panel(right_x, CONTENT_Y, col_w, panel_h)
        else:
            self._draw_algo_panel(right_x, CONTENT_Y, col_w, panel_h)

        btn_w, btn_h = 200, 44
        btn_x = (sw - btn_w) // 2
        btn_y = sh - 62
        self.start_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        pygame.draw.rect(self.screen, BTN_BG,  self.start_rect, border_radius=12)
        pygame.draw.rect(self.screen, BTN_BDR, self.start_rect, 2, border_radius=12)
        btn_lbl = self.font_btn.render(">  START  ( Enter )", True, BTN_TXT)
        bx = btn_x + (btn_w - btn_lbl.get_width())  // 2
        by = btn_y + (btn_h - btn_lbl.get_height()) // 2
        self.screen.blit(btn_lbl, (bx, by))

        if self.is_competitive:
            hint = "Up/Down: Map   |   Type numbers: Max Steps   |   Enter/Click: Start   |   Esc: Back"
        else:
            hint = "Up/Down: Map   |   Left/Right: Algorithm   |   Enter/Click: Confirm   |   Esc: Back"
        hint_surf = self.font_hint.render(hint, True, HINT_COLOR)
        self.screen.blit(hint_surf, ((sw - hint_surf.get_width()) // 2, sh - 20))

    def _draw_map_panel(self, x, y, w, h):
        pygame.draw.rect(self.screen, PANEL_BG,  (x, y, w, h), border_radius=12)
        pygame.draw.rect(self.screen, PANEL_BDR, (x, y, w, h), 1, border_radius=12)

        sec = self.font_sec.render("MAP", True, SUBTITLE)
        self.screen.blit(sec, (x + 14, y + 12))
        div_y = y + 12 + sec.get_height() + 6
        pygame.draw.line(self.screen, PANEL_BDR, (x + 10, div_y), (x + w - 10, div_y))

        row_h   = 38
        row_gap = 8
        row_x   = x + 10
        row_w   = w - 20
        self.map_rects = []

        for i, map_path in enumerate(self.map_paths):
            ry   = div_y + 8 + i * (row_h + row_gap)
            rect = pygame.Rect(row_x, ry, row_w, row_h)
            self.map_rects.append(rect)

            is_sel    = (i == self.selected_map)
            bg_color  = ROW_SELECT if is_sel else ROW_NORMAL
            bdr_color = ROW_BDR_S  if is_sel else ROW_BDR_N
            pygame.draw.rect(self.screen, bg_color,  rect, border_radius=8)
            pygame.draw.rect(self.screen, bdr_color, rect, 1, border_radius=8)

            name      = os.path.basename(map_path)
            txt_color = ROW_TXT_S if is_sel else ROW_TXT_N
            name_surf = self.font_row.render(name, True, txt_color)
            text_y    = ry + (row_h - name_surf.get_height()) // 2
            self.screen.blit(name_surf, (row_x + 12, text_y))

            if is_sel:
                arrow = self.font_row.render(">", True, GOLD)
                self.screen.blit(arrow, (row_x + row_w - 20, text_y))

    def _draw_algo_panel(self, x, y, w, h):
        btn_h   = 52
        btn_gap = 6
        n       = len(self.algorithms)
        algo_h  = 40 + 10 + n * (btn_h + btn_gap)
        info_h  = max(h - algo_h - 14, 60)

        pygame.draw.rect(self.screen, PANEL_BG,  (x, y, w, algo_h), border_radius=12)
        pygame.draw.rect(self.screen, PANEL_BDR, (x, y, w, algo_h), 1, border_radius=12)

        sec = self.font_sec.render("ALGORITHM", True, SUBTITLE)
        self.screen.blit(sec, (x + 14, y + 12))
        div_y = y + 12 + sec.get_height() + 6
        pygame.draw.line(self.screen, PANEL_BDR, (x + 10, div_y), (x + w - 10, div_y))

        self.algo_rects = []
        btn_x = x + 10
        btn_w = w - 20

        for i, key in enumerate(self.algorithms):
            label, full, note = ALGO_INFO.get(key, (key.upper(), "", ""))
            by    = div_y + 10 + i * (btn_h + btn_gap)
            brect = pygame.Rect(btn_x, by, btn_w, btn_h)
            self.algo_rects.append(brect)

            is_sel = (i == self.selected_algo)
            bg_c   = ALGO_SELECT if is_sel else ALGO_NORMAL
            bdr_c  = ALGO_BDR_S  if is_sel else ALGO_BDR_N
            pygame.draw.rect(self.screen, bg_c,  brect, border_radius=10)
            pygame.draw.rect(self.screen, bdr_c, brect, 2 if is_sel else 1, border_radius=10)

            lbl_c  = GOLD            if is_sel else ALGO_TXT_N
            note_c = (200, 195, 240) if is_sel else (100, 95, 150)
            self.screen.blit(self.font_algo.render(label, True, lbl_c),  (btn_x + 12, by + 4))
            self.screen.blit(self.font_small.render(full,  True, ALGO_TXT_N), (btn_x + 12, by + 24))
            self.screen.blit(self.font_small.render(note,  True, note_c),     (btn_x + 12, by + 38))

            if is_sel:
                ck = self.font_algo.render("v", True, GOLD)
                self.screen.blit(ck, (btn_x + btn_w - ck.get_width() - 10, by + (btn_h - ck.get_height()) // 2))

        info_y = y + algo_h + 14
        pygame.draw.rect(self.screen, PANEL_BG,  (x, info_y, w, info_h), border_radius=12)
        pygame.draw.rect(self.screen, PANEL_BDR, (x, info_y, w, info_h), 1, border_radius=12)

        sec2 = self.font_sec.render("SELECTION INFO", True, SUBTITLE)
        self.screen.blit(sec2, (x + 14, info_y + 12))
        div2 = info_y + 12 + sec2.get_height() + 6
        pygame.draw.line(self.screen, PANEL_BDR, (x + 10, div2), (x + w - 10, div2))

        map_name   = os.path.basename(self.map_paths[self.selected_map]) if self.map_paths else "-"
        algo_label = ALGO_INFO.get(self.algorithms[self.selected_algo], (self.algorithms[self.selected_algo].upper(),))[0]

        for idx, (lbl, val, col) in enumerate([
            ("Map  :", map_name,   (220, 215, 255)),
            ("Algo :", algo_label, GOLD),
        ]):
            ry2 = div2 + 10 + idx * 26
            self.screen.blit(self.font_small.render(lbl, True, HINT_COLOR), (x + 14, ry2))
            self.screen.blit(self.font_small.render(val, True, col),        (x + 70,  ry2))

    def _draw_competitive_panel(self, x, y, w, h):
        agent_h = 210
        match_h = max(h - agent_h - 14, 50)

        pygame.draw.rect(self.screen, PANEL_BG,  (x, y, w, agent_h), border_radius=12)
        pygame.draw.rect(self.screen, PANEL_BDR, (x, y, w, agent_h), 1, border_radius=12)

        sec = self.font_sec.render("AGENTS", True, SUBTITLE)
        self.screen.blit(sec, (x + 14, y + 12))
        div_y = y + 12 + sec.get_height() + 6
        pygame.draw.line(self.screen, PANEL_BDR, (x + 10, div_y), (x + w - 10, div_y))

        card_x = x + 10
        card_w = w - 20
        card_h = 58
        gap    = 6

        c1_y = div_y + 10
        c1   = pygame.Rect(card_x, c1_y, card_w, card_h)
        pygame.draw.rect(self.screen, (20, 30, 70), c1, border_radius=8)
        pygame.draw.rect(self.screen, AGENT1_COL,  c1, 2, border_radius=8)
        self.screen.blit(self.font_algo.render("Agent 1  (A*)",                           True, AGENT1_COL),     (card_x + 10, c1_y + 6))
        self.screen.blit(self.font_small.render("Algorithm: A* Chebyshev  |  agent_tan.py",  True, (130, 160, 230)), (card_x + 10, c1_y + 30))

        vs_surf = self.font_algo.render("VS", True, VS_COLOR)
        vs_y    = c1_y + card_h + gap
        self.screen.blit(vs_surf, (x + (w - vs_surf.get_width()) // 2, vs_y))

        c2_y = vs_y + vs_surf.get_height() + gap
        c2   = pygame.Rect(card_x, c2_y, card_w, card_h)
        pygame.draw.rect(self.screen, (20, 60, 35), c2, border_radius=8)
        pygame.draw.rect(self.screen, AGENT2_COL,  c2, 2, border_radius=8)
        self.screen.blit(self.font_algo.render("Agent 2  (UCS)",                              True, AGENT2_COL),     (card_x + 10, c2_y + 6))
        self.screen.blit(self.font_small.render("Algorithm: UCS             |  agent_hieu.py", True, (120, 210, 155)), (card_x + 10, c2_y + 30))

        badge = self.font_small.render("Time limit per step: 1,000 ms (enforced)", True, (200, 200, 100))
        self.screen.blit(badge, (x + (w - badge.get_width()) // 2, c2_y + card_h + 8))

        match_y = y + agent_h + 14
        pygame.draw.rect(self.screen, PANEL_BG,  (x, match_y, w, match_h), border_radius=12)
        pygame.draw.rect(self.screen, PANEL_BDR, (x, match_y, w, match_h), 1, border_radius=12)

        sec2 = self.font_sec.render("MATCH SETTINGS", True, SUBTITLE)
        self.screen.blit(sec2, (x + 14, match_y + 12))
        div2 = match_y + 12 + sec2.get_height() + 6
        pygame.draw.line(self.screen, PANEL_BDR, (x + 10, div2), (x + w - 10, div2))

        map_name = os.path.basename(self.map_paths[self.selected_map]) if self.map_paths else "-"

        ry_map = div2 + 12
        self.screen.blit(self.font_small.render("Map   :", True, HINT_COLOR),     (x + 14, ry_map))
        self.screen.blit(self.font_small.render(map_name,  True, (220, 215, 255)), (x + 75, ry_map))

        ry_step = ry_map + 28
        self.screen.blit(self.font_small.render("Steps :", True, HINT_COLOR), (x + 14, ry_step))

        box = pygame.Rect(x + 75, ry_step - 3, 80, 22)
        pygame.draw.rect(self.screen, (20, 25, 50),    box, border_radius=4)
        pygame.draw.rect(self.screen, (100, 100, 200), box, 1, border_radius=4)

        disp     = self.step_limit_str if self.step_limit_str else "50"
        val_surf = self.font_small.render(disp, True, (255, 255, 255))
        self.screen.blit(val_surf, (x + 79, ry_step))

        if (pygame.time.get_ticks() // 500) % 2 == 0:
            cx = x + 79 + val_surf.get_width() + 2
            pygame.draw.line(self.screen, (255, 255, 255), (cx, ry_step + 2), (cx, ry_step + 16), 1)

        if not self.step_limit_str:
            self.screen.blit(self.font_small.render("(default: 50)", True, (90, 90, 140)), (x + 162, ry_step))

    def get_selection(self):
        map_path = self.map_paths[self.selected_map]
        algo     = self.algorithms[self.selected_algo]
        if self.is_competitive:
            n_steps = int(self.step_limit_str) if self.step_limit_str else 50
            return map_path, algo, n_steps
        return map_path, algo