import pygame
import os


class MainMenuScreen:
    C_BG_TOP = (15,  20,  45)
    C_BG_BOT = (30,  15,  60)
    C_TITLE = (255, 215,  0)
    C_TITLE_SH = ( 80,  55,  0)
    C_SUB = (160, 155, 210)
    C_BTN_NOR = ( 35,  35,  72)
    C_BTN_SEL = ( 65,  40, 135)
    C_BDR_NOR = ( 75,  75, 150)
    C_BDR_SEL = (190, 145, 255)
    C_LBL_NOR = (180, 180, 220)
    C_LBL_SEL = (255, 255, 255)
    C_DESC_NOR = (110, 110, 155)
    C_DESC_SEL = (205, 195, 240)
    C_ARROW  = (255, 200,   0)
    C_HINT = ( 90,  90, 140)
    C_WHITE = (255, 255, 255)

    OPTIONS = [
        (
            "Single agent",
            "UCS/A* - Automated Search",
            "player.png",
        ),
        (
            "Two agents(Competitive)",
            "A* (Agent 1) vs UCS (Agent 2)",
            "player2.png",
        ),
    ]

    def __init__(self, screen: pygame.Surface, assets_dir: str):
        self.screen = screen
        self.selected  = 0
        self._btn_rects: list = []

        self.f_title = pygame.font.SysFont("arial", 60, bold=True)
        self.f_sub = pygame.font.SysFont("arial", 19)
        self.f_label = pygame.font.SysFont("arial", 32, bold=True)
        self.f_desc = pygame.font.SysFont("arial", 18)
        self.f_hint = pygame.font.SysFont("arial", 15)
        self.f_num = pygame.font.SysFont("arial", 44, bold=True)

        self._icons: list = []
        for _, _, fname in self.OPTIONS:
            path = os.path.join(assets_dir, 'sprites', fname)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                self._icons.append(pygame.transform.scale(img, (54, 54)))
            else:
                self._icons.append(None)

        sw, sh = screen.get_size()
        self._bg = pygame.Surface((sw, sh))
        for y in range(sh):
            t = y / sh
            r = int(self.C_BG_TOP[0] * (1-t) + self.C_BG_BOT[0] * t)
            g = int(self.C_BG_TOP[1] * (1-t) + self.C_BG_BOT[1] * t)
            b = int(self.C_BG_TOP[2] * (1-t) + self.C_BG_BOT[2] * t)
            pygame.draw.line(self._bg, (r, g, b), (0, y), (sw, y))

        dot_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
        for gx in range(0, sw, 36):
            for gy in range(0, sh, 36):
                pygame.draw.circle(dot_surf, (255, 255, 255, 18), (gx, gy), 1)
        self._bg.blit(dot_surf, (0, 0))

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.OPTIONS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.OPTIONS)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                return self.selected
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit

        elif event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self._btn_rects):
                if rect.collidepoint(event.pos):
                    self.selected = i

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self._btn_rects):
                if rect.collidepoint(event.pos):
                    self.selected = i
                    return i

        return None

    def draw(self):
        sw, sh = self.screen.get_size()
        self.screen.blit(self._bg, (0, 0))

        title_y = sh // 5
        shadow = self.f_title.render("SOKOBAN", True, self.C_TITLE_SH)
        title = self.f_title.render("SOKOBAN", True, self.C_TITLE)
        tx = (sw - title.get_width()) // 2
        self.screen.blit(shadow, (tx + 4, title_y + 4))
        self.screen.blit(title,  (tx, title_y))

        line_y = title_y + title.get_height() + 8
        pygame.draw.line(self.screen, self.C_TITLE, (tx, line_y), (tx + title.get_width(), line_y), 2)

        sub = self.f_sub.render("Hieu's Team - Sokoban Puzzle Solver - TDTU", True, self.C_SUB)
        self.screen.blit(sub, ((sw - sub.get_width()) // 2, line_y + 10))

        BTN_W = 480
        BTN_H = 100
        BTN_X = (sw - BTN_W) // 2
        GAP = 24
        btn_y_start = int(sh * 0.45)

        self._btn_rects = []
        for i, (label, desc, _) in enumerate(self.OPTIONS):
            rect   = pygame.Rect(BTN_X, btn_y_start + i * (BTN_H + GAP), BTN_W, BTN_H)
            is_sel = (i == self.selected)
            self._btn_rects.append(rect)

            if is_sel:
                glow      = rect.inflate(12, 12)
                glow_surf = pygame.Surface(glow.size, pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*self.C_BDR_SEL, 60), glow_surf.get_rect(), border_radius=22)
                self.screen.blit(glow_surf, glow.topleft)

            bg_c  = self.C_BTN_SEL if is_sel else self.C_BTN_NOR
            bdr_c = self.C_BDR_SEL if is_sel else self.C_BDR_NOR
            pygame.draw.rect(self.screen, bg_c,  rect, border_radius=18)
            pygame.draw.rect(self.screen, bdr_c, rect, 2, border_radius=18)

            icon = self._icons[i]
            icon_x = rect.left + 22
            if icon:
                self.screen.blit(icon, (icon_x, rect.top + (BTN_H - 54) // 2))

            num_c = self.C_ARROW if is_sel else self.C_BDR_NOR
            num = self.f_num.render(str(i + 1), True, num_c)
            self.screen.blit(num, (icon_x + 60, rect.top + (BTN_H - num.get_height()) // 2))

            text_x = icon_x + 110
            lbl_c = self.C_LBL_SEL  if is_sel else self.C_LBL_NOR
            dsc_c = self.C_DESC_SEL if is_sel else self.C_DESC_NOR
            lbl = self.f_label.render(label, True, lbl_c)
            dsc = self.f_desc.render(desc,   True, dsc_c)
            self.screen.blit(lbl, (text_x, rect.top + 22))
            self.screen.blit(dsc, (text_x, rect.top + 58))

            if is_sel:
                arrow = self.f_label.render(">", True, self.C_ARROW)
                self.screen.blit(arrow, (BTN_X - 28, rect.top + (BTN_H - arrow.get_height()) // 2))
     
        hint = self.f_hint.render(
            "Up/Down: Navigate | Enter/Click: Confirm | Esc: Quit",
            True, self.C_HINT,
        )
        self.screen.blit(hint, ((sw - hint.get_width()) // 2, sh - 32))
