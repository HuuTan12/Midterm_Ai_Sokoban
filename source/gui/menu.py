import pygame
import os


_BG_TOP    = (15,  20,  45)
_BG_BOT    = (30,  15,  60)
_GOLD      = (255, 215,   0)
_GOLD_DIM  = ( 80,  55,   0)
_SUBTITLE  = (160, 155, 210)
_HINT      = ( 90,  90, 140)
_PANEL_BG  = ( 25,  25,  55)
_PANEL_BDR = ( 65,  65, 130)
_ROW_NOR   = ( 35,  35,  72)
_ROW_SEL   = ( 65,  40, 135)
_ROW_BDR_N = ( 60,  60, 120)
_ROW_BDR_S = (190, 145, 255)
_ROW_TXT_N = (175, 175, 215)
_ROW_TXT_S = (255, 255, 255)
_ALGO_NOR  = ( 40,  40,  85)
_ALGO_SEL  = ( 90,  55, 170)
_ALGO_BDR_N= ( 70,  70, 140)
_ALGO_BDR_S= (220, 170, 255)
_ALGO_TXT_N= (160, 155, 210)
_ALGO_TXT_S= (255, 255, 255)
_ENTER_BG  = ( 50, 130,  70)
_ENTER_BDR = (100, 220, 130)
_ENTER_TXT = (220, 255, 230)

_ALGO_META = {
    "ucs": {
        "label": "UCS",
        "full":  "Uniform Cost Search",
        "note":  "Search by increasing cost",
    },
    "astar": {
        "label": "A*",
        "full":  "A* (Chebyshev Heuristic)",
        "note":  "Heuristic-guided optimal search",
    },
    "bfs": {
        "label": "BFS",
        "full":  "Breadth-First Search",
        "note":  "Shortest path by number of steps",
    },
    "gbfs": {
        "label": "GBFS",
        "full":  "Greedy Best-First Search",
        "note":  "Fast but not guaranteed optimal",
    },
}


class MenuScreen:
    def __init__(self, screen: pygame.Surface, map_paths: list, is_competitive: bool = False):
        self.screen              = screen
        self.map_paths           = map_paths
        self.is_competitive      = is_competitive
        self.selected_map_index  = 0
        self.algorithms          = ["ucs", "astar", "bfs", "gbfs"]
        self.selected_algo_index = 0
        self.is_confirmed        = False
        self.step_limit_str      = ""

        self.f_title = pygame.font.SysFont("arial", 44, bold=True)
        self.f_sub   = pygame.font.SysFont("arial", 17)
        self.f_sec   = pygame.font.SysFont("arial", 15, bold=True)
        self.f_row   = pygame.font.SysFont("arial", 19, bold=True)
        self.f_algo  = pygame.font.SysFont("arial", 22, bold=True)
        self.f_note  = pygame.font.SysFont("arial", 14)
        self.f_enter = pygame.font.SysFont("arial", 20, bold=True)
        self.f_hint  = pygame.font.SysFont("arial", 14)

        sw, sh = screen.get_size()
        self._bg = pygame.Surface((sw, sh))
        for y in range(sh):
            t = y / sh
            r = int(_BG_TOP[0] * (1-t) + _BG_BOT[0] * t)
            g = int(_BG_TOP[1] * (1-t) + _BG_BOT[1] * t)
            b = int(_BG_TOP[2] * (1-t) + _BG_BOT[2] * t)
            pygame.draw.line(self._bg, (r, g, b), (0, y), (sw, y))

        dot_s = pygame.Surface((sw, sh), pygame.SRCALPHA)
        for gx in range(0, sw, 36):
            for gy in range(0, sh, 36):
                pygame.draw.circle(dot_s, (255, 255, 255, 15), (gx, gy), 1)
        self._bg.blit(dot_s, (0, 0))

        self._map_rects : list = []
        self._algo_rects: list = []
        self._enter_rect       = None

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_map_index = (self.selected_map_index - 1) % max(len(self.map_paths), 1)
            elif event.key == pygame.K_DOWN:
                self.selected_map_index = (self.selected_map_index + 1) % max(len(self.map_paths), 1)
            elif event.key == pygame.K_LEFT:
                self.selected_algo_index = (self.selected_algo_index - 1) % len(self.algorithms)
            elif event.key == pygame.K_RIGHT:
                self.selected_algo_index = (self.selected_algo_index + 1) % len(self.algorithms)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.is_confirmed = True
                return True
            elif self.is_competitive:
                if event.key == pygame.K_BACKSPACE:
                    self.step_limit_str = self.step_limit_str[:-1]
                elif event.unicode.isdigit():
                    self.step_limit_str += event.unicode
                    if len(self.step_limit_str) > 3:
                        self.step_limit_str = self.step_limit_str[:3]

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for i, rect in enumerate(self._map_rects):
                if rect.collidepoint(pos):
                    self.selected_map_index = i
                    break
            for i, rect in enumerate(self._algo_rects):
                if rect.collidepoint(pos):
                    self.selected_algo_index = i
                    break
            if self._enter_rect and self._enter_rect.collidepoint(pos):
                self.is_confirmed = True
                return True

        elif event.type == pygame.MOUSEMOTION:
            pos = event.pos
            for i, rect in enumerate(self._map_rects):
                if rect.collidepoint(pos):
                    self.selected_map_index = i
                    break

        return False

    def draw(self):
        sw, sh = self.screen.get_size()
        self.screen.blit(self._bg, (0, 0))

        TITLE_Y = 28
        sh_surf = self.f_title.render("CHOOSE MAP & ALGORITHM", True, _GOLD_DIM)
        ti_surf = self.f_title.render("CHOOSE MAP & ALGORITHM", True, _GOLD)
        tx = (sw - ti_surf.get_width()) // 2
        self.screen.blit(sh_surf, (tx + 3, TITLE_Y + 3))
        self.screen.blit(ti_surf, (tx, TITLE_Y))

        line_y = TITLE_Y + ti_surf.get_height() + 4
        pygame.draw.line(self.screen, _GOLD, (tx, line_y), (tx + ti_surf.get_width(), line_y), 2)

        sub = self.f_sub.render(
            "Up/Down: select Map   |   Left/Right: select Algorithm   |   Enter / Click: Confirm",
            True, _SUBTITLE
        )
        self.screen.blit(sub, ((sw - sub.get_width()) // 2, line_y + 6))

        COL_GAP   = 28
        LEFT_W    = int(sw * 0.52)
        RIGHT_W   = sw - LEFT_W - COL_GAP * 2
        LEFT_X    = COL_GAP
        RIGHT_X   = LEFT_W + COL_GAP * 2
        CONTENT_Y = TITLE_Y + ti_surf.get_height() + 40

        MAP_PANEL_H = sh - CONTENT_Y - 80
        map_panel   = pygame.Rect(LEFT_X, CONTENT_Y, LEFT_W, MAP_PANEL_H)
        pygame.draw.rect(self.screen, _PANEL_BG,  map_panel, border_radius=16)
        pygame.draw.rect(self.screen, _PANEL_BDR, map_panel, 1, border_radius=16)

        sec_map = self.f_sec.render("MAP", True, _SUBTITLE)
        self.screen.blit(sec_map, (LEFT_X + 16, CONTENT_Y + 12))

        DIVIDER_Y = CONTENT_Y + 12 + sec_map.get_height() + 8
        pygame.draw.line(self.screen, _PANEL_BDR,
                         (LEFT_X + 12, DIVIDER_Y), (LEFT_X + LEFT_W - 12, DIVIDER_Y))

        ROW_H   = 38
        ROW_PAD = 8
        ROW_X   = LEFT_X + 10
        ROW_W   = LEFT_W - 20
        self._map_rects = []

        for i, mp in enumerate(self.map_paths):
            ry    = DIVIDER_Y + 8 + i * (ROW_H + ROW_PAD)
            rrect = pygame.Rect(ROW_X, ry, ROW_W, ROW_H)
            self._map_rects.append(rrect)

            is_sel = (i == self.selected_map_index)
            bg     = _ROW_SEL   if is_sel else _ROW_NOR
            bdr    = _ROW_BDR_S if is_sel else _ROW_BDR_N
            pygame.draw.rect(self.screen, bg,  rrect, border_radius=10)
            pygame.draw.rect(self.screen, bdr, rrect, 1, border_radius=10)

            name  = os.path.basename(mp)
            txt_c = _ROW_TXT_S if is_sel else _ROW_TXT_N
            txt   = self.f_row.render(name, True, txt_c)
            ty    = ry + (ROW_H - txt.get_height()) // 2
            self.screen.blit(txt, (ROW_X + 14, ty))

            if is_sel:
                arrow = self.f_row.render(">", True, _GOLD)
                self.screen.blit(arrow, (ROW_X + ROW_W - 22, ty))

        ABTN_H      = 52
        ABTN_GAP    = 6
        ABTN_W      = RIGHT_W - 20
        ABTN_X      = RIGHT_X + 10
        n_algos     = len(self.algorithms)
        ALGO_HDR_H  = 40
        ALGO_PANEL_H= ALGO_HDR_H + 12 + n_algos * (ABTN_H + ABTN_GAP) + 4

        algo_panel = pygame.Rect(RIGHT_X, CONTENT_Y, RIGHT_W, ALGO_PANEL_H)
        pygame.draw.rect(self.screen, _PANEL_BG,  algo_panel, border_radius=16)
        pygame.draw.rect(self.screen, _PANEL_BDR, algo_panel, 1, border_radius=16)

        sec_algo = self.f_sec.render("ALGORITHM", True, _SUBTITLE)
        self.screen.blit(sec_algo, (RIGHT_X + 16, CONTENT_Y + 12))

        ALGO_DIV_Y = CONTENT_Y + 12 + sec_algo.get_height() + 8
        pygame.draw.line(self.screen, _PANEL_BDR,
                         (RIGHT_X + 12, ALGO_DIV_Y), (RIGHT_X + RIGHT_W - 12, ALGO_DIV_Y))

        ABTN_Y_START = ALGO_DIV_Y + 12
        self._algo_rects = []

        for i, algo_key in enumerate(self.algorithms):
            meta  = _ALGO_META.get(algo_key, {"label": algo_key.upper(), "full": "", "note": ""})
            ay    = ABTN_Y_START + i * (ABTN_H + ABTN_GAP)
            arect = pygame.Rect(ABTN_X, ay, ABTN_W, ABTN_H)
            self._algo_rects.append(arect)

            is_sel = (i == self.selected_algo_index)
            bg     = _ALGO_SEL   if is_sel else _ALGO_NOR
            bdr    = _ALGO_BDR_S if is_sel else _ALGO_BDR_N
            pygame.draw.rect(self.screen, bg,  arect, border_radius=12)
            pygame.draw.rect(self.screen, bdr, arect, 2 if is_sel else 1, border_radius=12)

            if is_sel:
                gl = arect.inflate(10, 10)
                gs = pygame.Surface(gl.size, pygame.SRCALPHA)
                pygame.draw.rect(gs, (*_ALGO_BDR_S, 50), gs.get_rect(), border_radius=16)
                self.screen.blit(gs, gl.topleft)

            txt_c  = _ALGO_TXT_S if is_sel else _ALGO_TXT_N
            note_c = (190, 185, 230) if is_sel else (100, 95, 150)
            lbl    = self.f_algo.render(meta["label"], True, _GOLD if is_sel else txt_c)
            full   = self.f_note.render(meta["full"],  True, txt_c)
            note   = self.f_note.render(meta["note"],  True, note_c)
            self.screen.blit(lbl,  (ABTN_X + 14, ay + 5))
            self.screen.blit(full, (ABTN_X + 14, ay + 24))
            self.screen.blit(note, (ABTN_X + 14, ay + 38))

            if is_sel:
                ck = self.f_algo.render("v", True, _GOLD)
                self.screen.blit(ck, (ABTN_X + ABTN_W - ck.get_width() - 12,
                                       ay + (ABTN_H - ck.get_height()) // 2))

        INFO_Y = CONTENT_Y + ALGO_PANEL_H + 16
        INFO_H = sh - INFO_Y - 70
        if INFO_H > 50:
            info_panel = pygame.Rect(RIGHT_X, INFO_Y, RIGHT_W, INFO_H)
            pygame.draw.rect(self.screen, _PANEL_BG,  info_panel, border_radius=16)
            pygame.draw.rect(self.screen, _PANEL_BDR, info_panel, 1, border_radius=16)

            sec_info = self.f_sec.render("SELECTION INFO", True, _SUBTITLE)
            self.screen.blit(sec_info, (RIGHT_X + 16, INFO_Y + 12))

            map_name = os.path.basename(self.map_paths[self.selected_map_index]) if self.map_paths else "-"
            algo_key = self.algorithms[self.selected_algo_index]
            meta     = _ALGO_META.get(algo_key, {"label": algo_key.upper()})

            lines = [
                ("Map   :", map_name,       (220, 215, 255)),
                ("Algo  :", meta["label"],   _GOLD),
            ]
            
            if self.is_competitive:
                disp_val = self.step_limit_str if self.step_limit_str else "50 (default)"
                lines.append(("Steps :", disp_val, (100, 255, 100)))

            for row_i, (lbl, val, vc) in enumerate(lines):
                ly     = INFO_Y + 34 + row_i * 24
                l_surf = self.f_note.render(lbl, True, _HINT)
                self.screen.blit(l_surf, (RIGHT_X + 16, ly))
                
                if lbl == "Steps :":
                    # Draw visual input box
                    box_rect = pygame.Rect(RIGHT_X + 80, ly - 3, 100, 24)
                    pygame.draw.rect(self.screen, (20, 25, 50), box_rect, border_radius=4)
                    pygame.draw.rect(self.screen, (100, 100, 200), box_rect, 1, border_radius=4)
                    
                    disp_val = self.step_limit_str if self.step_limit_str else "50"
                    v_surf = self.f_note.render(disp_val, True, (255, 255, 255))
                    self.screen.blit(v_surf, (RIGHT_X + 86, ly))
                    
                    # Blinking cursor
                    if (pygame.time.get_ticks() // 500) % 2 == 0:
                        cx = RIGHT_X + 86 + v_surf.get_width() + 2
                        pygame.draw.line(self.screen, (255, 255, 255), (cx, ly + 2), (cx, ly + 18), 2)
                else:
                    v_surf = self.f_note.render(val, True, vc)
                    self.screen.blit(v_surf, (RIGHT_X + 80, ly))

        ENT_W, ENT_H = 220, 46
        ENT_X = RIGHT_X + (RIGHT_W - ENT_W) // 2
        ENT_Y = sh - 62
        self._enter_rect = pygame.Rect(ENT_X, ENT_Y, ENT_W, ENT_H)

        gl2 = self._enter_rect.inflate(12, 12)
        gs2 = pygame.Surface(gl2.size, pygame.SRCALPHA)
        pygame.draw.rect(gs2, (*_ENTER_BDR, 60), gs2.get_rect(), border_radius=16)
        self.screen.blit(gs2, gl2.topleft)

        pygame.draw.rect(self.screen, _ENTER_BG,  self._enter_rect, border_radius=14)
        pygame.draw.rect(self.screen, _ENTER_BDR, self._enter_rect, 2, border_radius=14)
        ent_txt = self.f_enter.render(">  START  ( Enter )", True, _ENTER_TXT)
        ex = ENT_X + (ENT_W - ent_txt.get_width())  // 2
        ey = ENT_Y + (ENT_H - ent_txt.get_height()) // 2
        self.screen.blit(ent_txt, (ex, ey))

        hint_txt = "Up/Down: Map   |   Left/Right: Algo   |   Enter / Click: Confirm   |   Esc: Back"
        if self.is_competitive:
            hint_txt = "Type numbers to set Max Steps   |   " + hint_txt

        hint = self.f_hint.render(hint_txt, True, _HINT)
        self.screen.blit(hint, ((sw - hint.get_width()) // 2, sh - 22))

    def get_selection(self):
        map_path = self.map_paths[self.selected_map_index]
        algo = self.algorithms[self.selected_algo_index]
        if self.is_competitive:
            step_limit = int(self.step_limit_str) if self.step_limit_str else 50
            return map_path, algo, step_limit
        return map_path, algo