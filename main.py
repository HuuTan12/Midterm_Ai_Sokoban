"""
main.py — Ứng dụng Sokoban AI thống nhất trong MỘT cửa sổ pygame duy nhất.

Luồng trạng thái:
  MAIN_MENU
    ↓ chọn chế độ
  SINGLE_GAME  (menu map + thuật toán → giải → phát lại, tất cả trong Game object)
    hoặc
  COMP_MENU    (menu map cho chế độ 2 agent)
    ↓ xác nhận
  COMP_SOLVING (đang tính toán, hiển thị loading)
    ↓ xong
  COMP_GAME    (phát lại competitive, điều khiển bằng phím)
    ↓ Esc
  MAIN_MENU
"""

import pygame
import sys
import os
import threading

# ── sys.path ──────────────────────────────────────────────────────────
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
SRC_DIR  = os.path.join(ROOT_DIR, 'source')
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, SRC_DIR)

# ── Import sau khi path đã set ─────────────────────────────────────────
from source.gui.main_menu  import MainMenuScreen
from source.gui.menu       import MenuScreen
from source.gui.game       import Game, AppState
from source.gui.controls   import Command, map_event_to_command


# ── Hằng số ──────────────────────────────────────────────────────────
SCREEN_W  = 900
SCREEN_H  = 650
FPS       = 60
TITLE     = "Sokoban AI  -  Nhom Hieu  -  TDTU"


# ── Hàm tiện ích ──────────────────────────────────────────────────────
def _get_maps(maps_dir: str) -> list[str]:
    if not os.path.exists(maps_dir):
        return []
    return [
        os.path.join(maps_dir, f)
        for f in sorted(os.listdir(maps_dir))
        if f.endswith(".txt")
    ]


def _is_competitive(path: str) -> bool:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return 'A' in content and 'E' in content
    except Exception:
        return False


def _draw_loading(screen: pygame.Surface, font: pygame.font.Font):
    """Vẽ màn hình 'Đang tính toán...' cho chế độ competitive."""
    screen.fill((20, 20, 45))
    sw, sh = screen.get_size()
    txt = font.render("Dang tinh toan loi giai...  Vui long doi.", True, (255, 215, 0))
    hint = pygame.font.SysFont("arial", 18).render(
        "A* (Agent 1)  vs  UCS (Agent 2)  -  Chebyshev Heuristic", True, (140, 135, 200)
    )
    screen.blit(txt,  ((sw - txt.get_width())  // 2, sh // 2 - 30))
    screen.blit(hint, ((sw - hint.get_width()) // 2, sh // 2 + 20))


# ── Lớp ứng dụng chính ────────────────────────────────────────────────
class SokobanApp:
    """
    Quản lý toàn bộ vòng lặp pygame và chuyển trạng thái giữa các màn hình.
    Chỉ có MỘT cửa sổ pygame duy nhất từ đầu đến cuối.
    """

    S_MAIN_MENU   = "main_menu"
    S_SINGLE      = "single"         # Game object tự quản lý sub-state
    S_COMP_MENU   = "comp_menu"
    S_COMP_SOLVE  = "comp_solving"
    S_COMP_GAME   = "comp_game"

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption(TITLE)
        self.clock  = pygame.time.Clock()

        # Assets
        maps_dir   = os.path.join(ROOT_DIR, "source", "maps")
        assets_dir = os.path.join(ROOT_DIR, "source", "assets")
        all_maps   = _get_maps(maps_dir)
        single_maps= all_maps                               # tất cả map đều dùng được cho single
        comp_maps  = [m for m in all_maps if _is_competitive(m)]

        # Fonts dùng chung
        self._font_big  = pygame.font.SysFont("arial", 28, bold=True)
        self._font_hint = pygame.font.SysFont("arial", 18)

        # ── Màn hình ──
        self._main_menu  = MainMenuScreen(self.screen, assets_dir)
        self._single_maps  = single_maps
        self._comp_maps    = comp_maps
        self._comp_menu  : MenuScreen | None            = None  # tạo khi cần
        self._game       : Game | None                  = None
        self._comp_game                                 = None
        self._comp_thread: threading.Thread | None      = None
        self._comp_result                               = None  # (actions1, actions2, map_path)

        self._state = self.S_MAIN_MENU

    # ── Chuyển trạng thái ──────────────────────────────────────────────
    def _go_main_menu(self):
        self._state    = self.S_MAIN_MENU
        self._game     = None
        self._comp_game= None
        self._comp_result = None

    def _go_single(self):
        """Tạo đối tượng Game với screen hiện tại và chuyển sang chế độ single."""
        self._game  = Game(self.screen, self._single_maps)
        self._state = self.S_SINGLE

    def _go_comp_menu(self):
        if not self._comp_maps:
            # Không có map competitive → thông báo rồi trở về
            self._show_error("Khong co map 2 agents! (Can co ky tu 'E')")
            return
        self._comp_menu = MenuScreen(self.screen, self._comp_maps)
        self._state = self.S_COMP_MENU

    def _start_comp_solving(self, map_path: str, algorithm: str):
        """Chạy thuật toán competitive trong thread nền."""
        self._comp_result = None
        self._state       = self.S_COMP_SOLVE

        def worker():
            from source.core.map_parser import MapParser
            from source.core.competitive_rules import CompetitiveRules
            from source.search.agent_tan import AgentTan
            from source.search.agent_hieu import AgentHieu

            map_lines = MapParser.load_map(map_path)
            board, state = MapParser.parse_competitive_level(map_lines)

            agent1, agent2 = AgentTan(), AgentHieu()
            actions1, actions2 = [], []

            for _ in range(60):
                a1 = agent1.get_action(state, board)
                a2 = agent2.get_action(state, board)
                if a1 is None and a2 is None:
                    break
                actions1.append(a1)
                actions2.append(a2)
                state = CompetitiveRules.apply_actions(state, a1, a2, board)

            self._comp_result = (actions1, actions2, map_path)

        self._comp_thread = threading.Thread(target=worker, daemon=True)
        self._comp_thread.start()

    def _show_error(self, msg: str):
        """Hiển thị thông báo lỗi 2 giây rồi về main menu."""
        self.screen.fill((30, 15, 15))
        t = self._font_big.render(msg, True, (220, 60, 60))
        sw, sh = self.screen.get_size()
        self.screen.blit(t, ((sw - t.get_width()) // 2, sh // 2))
        pygame.display.flip()
        pygame.time.wait(2000)

    # ── Xử lý sự kiện ─────────────────────────────────────────────────
    def _handle_event(self, event: pygame.event.Event):
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        # ── Main Menu ──
        if self._state == self.S_MAIN_MENU:
            mode = self._main_menu.handle_event(event)
            if mode == 0:
                self._go_single()
            elif mode == 1:
                self._go_comp_menu()

        # ── Single: chuyển event cho Game object ──
        elif self._state == self.S_SINGLE:
            if self._game.state == AppState.MENU:
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                confirmed = self._game.menu.handle_event(event)
                if confirmed:
                    self._game.start_solving()
            else:
                cmd = map_event_to_command(event)
                if cmd:
                    self._game.apply_command(cmd)

        # ── Competitive Menu ──
        elif self._state == self.S_COMP_MENU:
            if self._comp_menu:
                confirmed = self._comp_menu.handle_event(event)
                if confirmed:
                    map_path, algo = self._comp_menu.get_selection()
                    self._start_comp_solving(map_path, algo)
            # Esc quay lại main menu
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._go_main_menu()

        # ── Comp Game ──
        elif self._state == self.S_COMP_GAME:
            if self._comp_game:
                result = self._comp_game.handle_event(event)
                if result == "BACK_TO_MENU":
                    self._go_main_menu()

    # ── Cập nhật logic ─────────────────────────────────────────────────
    def _update(self, now_ms: int):
        if self._state == self.S_SINGLE and self._game:
            if self._game.state == AppState.BACK:
                # Game báo quay về main menu
                self._go_main_menu()
                return
            if self._game.state == AppState.SOLVING:
                self._game.poll_search_result()
            elif self._game.state == AppState.PLAYING:
                self._game.auto_advance(now_ms)

        elif self._state == self.S_COMP_SOLVE:
            if self._comp_result is not None:
                # Kết quả đã có → tạo CompetitiveGameScreen
                from source.competitive_gui.game import CompetitiveGameScreen
                actions1, actions2, map_path = self._comp_result
                self._comp_game = CompetitiveGameScreen(self.screen, map_path, actions1, actions2)
                self._state = self.S_COMP_GAME

        elif self._state == self.S_COMP_GAME and self._comp_game:
            self._comp_game.update()

    # ── Vẽ ────────────────────────────────────────────────────────────
    def _draw(self):
        if self._state == self.S_MAIN_MENU:
            self._main_menu.draw()

        elif self._state == self.S_SINGLE and self._game:
            self._game.draw()

        elif self._state == self.S_COMP_MENU and self._comp_menu:
            self._comp_menu.draw()

        elif self._state == self.S_COMP_SOLVE:
            _draw_loading(self.screen, self._font_big)

        elif self._state == self.S_COMP_GAME and self._comp_game:
            self._comp_game.draw()

        pygame.display.flip()   # flip DUY NHẤT ở đây

    # ── Vòng lặp chính ────────────────────────────────────────────────
    def run(self):
        while True:
            now = pygame.time.get_ticks()
            for event in pygame.event.get():
                self._handle_event(event)
            self._update(now)
            self._draw()
            self.clock.tick(FPS)


# ── Entry point ───────────────────────────────────────────────────────
if __name__ == "__main__":
    SokobanApp().run()