import pygame
import sys
import os
import time
import threading

# Thêm thư mục gốc vào sys.path để import được core, search
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC_DIR  = os.path.join(ROOT_DIR, 'source')
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, SRC_DIR)

from source.gui.menu     import MenuScreen
from source.gui.renderer import Renderer
from source.gui.controls import Command, map_event_to_command


# ===== Các trạng thái của ứng dụng =====
class AppState:
    MENU        = "menu"
    SOLVING     = "solving"       # Đang chạy thuật toán (nền)
    PLAYING     = "playing"       # Đang phát lại lời giải
    NO_SOLUTION = "no_solution"
    BACK        = "back"          # Tín hiệu quay về menu chính


class Game:
    """
    Lớp Game điều phối toàn bộ vòng lặp game theo mô hình OOP:
      - Trạng thái MENU  → MenuScreen xử lý
      - Trạng thái SOLVING → chạy UCS/A* trong thread riêng
      - Trạng thái PLAYING → Renderer vẽ, controls điều khiển
    Có thể dùng độc lập (gọi run()) hoặc nhúng vào app ngoài (gọi handle_event/update/draw).
    """

    PLAYBACK_SPEED_MS = 300  # Millisecond giữa mỗi bước tự động

    def __init__(self, screen: pygame.Surface, map_paths: list):
        """
        screen    : pygame.Surface — cửa sổ pygame từ bên ngoài truyền vào
        map_paths : list[str]      — danh sách đường dẫn file map
        """
        self.screen = screen
        self.clock  = pygame.time.Clock()

        self.state = AppState.MENU
        self.menu  = MenuScreen(self.screen, map_paths)

        # Phát lại lời giải
        self.renderer        = None
        self.states_history  = []   # list[State]
        self.current_step    = 0
        self.paused          = True
        self._last_tick      = 0
        self.result_info     = {}

        # Dùng để truyền kết quả từ thread tìm kiếm
        self._search_result  = None  # None = chưa có / tuple(path, cost, expanded, max_q) / "no_solution"
        self._search_lock    = threading.Lock()

    # ─────────────────────────────────────────────
    # 1. Bắt đầu tìm kiếm (chạy trên thread riêng)
    # ─────────────────────────────────────────────
    def start_solving(self):
        from source.core.map_parser import MapParser
        from source.search.ucs   import UCS
        from source.search.astar import AStar
        from source.search.bfs   import BFS
        from source.search.gbfs  import GBFS

        map_path, algorithm = self.menu.get_selection()

        map_lines = MapParser.load_map(map_path)
        board, start_state = MapParser.parse_level(map_lines)

        # Lưu lại để dùng khi vẽ
        self._board       = board
        self._start_state = start_state
        self._algorithm   = algorithm
        self._search_result = None

        def worker():
            t0 = time.time()
            if algorithm == "ucs":
                solver = UCS()
            elif algorithm == "astar":
                solver = AStar()
            elif algorithm == "bfs":
                solver = BFS()
            elif algorithm == "gbfs":
                solver = GBFS()
            else:
                solver = AStar()   # fallback
            path, cost, expanded, max_q = solver.search(start_state, board, timeout_seconds=30.0)
            elapsed = time.time() - t0
            with self._search_lock:
                if path is not None:
                    self._search_result = (path, cost, expanded, max_q, elapsed)
                else:
                    self._search_result = "no_solution"

        threading.Thread(target=worker, daemon=True).start()
        self.state = AppState.SOLVING


    # ─────────────────────────────────────────────
    # 2. Kiểm tra kết quả tìm kiếm
    # ─────────────────────────────────────────────
    def poll_search_result(self):
        with self._search_lock:
            result = self._search_result

        if result is None:
            return  # Chưa xong

        if result == "no_solution":
            self.state = AppState.NO_SOLUTION
            return

        path, cost, expanded, max_q, elapsed = result

        # Xây dựng danh sách tất cả trạng thái từ đầu đến cuối
        from source.core.rules import Rules
        states = [self._start_state]
        current = self._start_state
        for action_str in path:
            for succ_action, succ_state in Rules.get_successors(current, self._board):
                if succ_action == action_str:
                    states.append(succ_state)
                    current = succ_state
                    break

        self.states_history = states
        self.renderer = Renderer(self.screen, self._board)
        self.current_step = 0
        self.paused = True
        self._last_tick = pygame.time.get_ticks()

        self.result_info = {
            "algorithm"   : self._algorithm,
            "total_steps" : len(path),
            "cost"        : cost,
            "expanded"    : expanded,
            "status"      : "paused",
        }
        self.state = AppState.PLAYING

    # ─────────────────────────────────────────────
    # 3. Xử lý lệnh điều khiển
    # ─────────────────────────────────────────────
    def apply_command(self, cmd):
        if cmd == Command.QUIT:
            pygame.quit()
            sys.exit()

        # Esc tại màn hình menu trong chế độ nhúng → gửi tín hiệu BACK về app ngoài
        if self.state == AppState.MENU:
            if cmd == Command.BACK_TO_MENU:
                self.state = AppState.BACK
            return

        if self.state == AppState.NO_SOLUTION:
            if cmd == Command.BACK_TO_MENU:
                self.state = AppState.MENU
            return

        if self.state != AppState.PLAYING:
            if cmd == Command.BACK_TO_MENU:
                self.state = AppState.MENU
            return

        if cmd == Command.TOGGLE_PAUSE:
            self.paused = not self.paused
            self._last_tick = pygame.time.get_ticks()

        elif cmd == Command.STEP_FORWARD:
            self.paused = True
            self.current_step = min(self.current_step + 1, len(self.states_history) - 1)

        elif cmd == Command.STEP_BACKWARD:
            self.paused = True
            self.current_step = max(self.current_step - 1, 0)

        elif cmd == Command.BACK_TO_MENU:
            self.state = AppState.MENU

    # ─────────────────────────────────────────────
    # 4. Tự động tiến bước khi đang play
    # ─────────────────────────────────────────────
    def auto_advance(self, now_ms):
        if self.paused:
            return
        if self.current_step >= len(self.states_history) - 1:
            self.paused = True
            return
        if now_ms - self._last_tick >= self.PLAYBACK_SPEED_MS:
            self.current_step += 1
            self._last_tick = now_ms

    # ─────────────────────────────────────────────
    # 5. Vẽ frame
    # ─────────────────────────────────────────────
    def draw(self):
        """Vẽ frame hiện tại. KHÔNG gọi pygame.display.flip() — để app ngoài gọi."""
        if self.state == AppState.MENU:
            self.menu.draw()

        elif self.state == AppState.SOLVING:
            self.screen.fill((30, 30, 30))
            font = pygame.font.SysFont("arial", 30)
            text = font.render("Dang tinh toan loi giai... Vui long doi.", True, (255, 220, 0))
            sw, sh = self.screen.get_size()
            self.screen.blit(text, ((sw - text.get_width()) // 2, sh // 2 - 20))

        elif self.state == AppState.NO_SOLUTION:
            self.screen.fill((30, 30, 30))
            font = pygame.font.SysFont("arial", 30)
            t1 = font.render("Khong tim duoc loi giai!", True, (220, 50, 50))
            t2 = font.render("Nhan Esc de quay lai menu chinh.", True, (200, 200, 200))
            sw, sh = self.screen.get_size()
            self.screen.blit(t1, ((sw - t1.get_width()) // 2, sh // 2 - 30))
            self.screen.blit(t2, ((sw - t2.get_width()) // 2, sh // 2 + 10))

        elif self.state == AppState.PLAYING:
            total  = len(self.states_history) - 1
            at_end = (self.current_step >= total)
            status = "solved" if at_end else ("paused" if self.paused else "playing")

            info = dict(self.result_info, step=self.current_step, status=status)

            self.renderer.draw_static()
            self.renderer.draw_state(self.states_history[self.current_step])
            self.renderer.draw_panel(info)

    # ─────────────────────────────────────────────
    # 6. Vòng lặp chính
    # ─────────────────────────────────────────────
    def run(self):
        """Vòng lặp độc lập — dùng khi chạy game.py trực tiếp."""
        while True:
            now = pygame.time.get_ticks()

            for event in pygame.event.get():
                if self.state == AppState.MENU:
                    if event.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    confirmed = self.menu.handle_event(event)
                    if confirmed:
                        self.start_solving()
                else:
                    cmd = map_event_to_command(event)
                    if cmd:
                        self.apply_command(cmd)
                    # BACK trong standalone → quay về menu nội bộ
                    if self.state == AppState.BACK:
                        self.state = AppState.MENU
                        self.menu.is_confirmed = False

            if self.state == AppState.SOLVING:
                self.poll_search_result()
            elif self.state == AppState.PLAYING:
                self.auto_advance(now)

            self.draw()
            pygame.display.flip()   # standalone: flip tại đây
            self.clock.tick(60)


# ─────────────────────────────────────────────
# Entry point khi chạy file này trực tiếp
# ─────────────────────────────────────────────
def main():
    pygame.init()
    maps_dir  = os.path.join(ROOT_DIR, "source", "maps")
    map_paths = [
        os.path.join(maps_dir, f)
        for f in sorted(os.listdir(maps_dir))
        if f.endswith(".txt")
    ] if os.path.exists(maps_dir) else []

    screen = pygame.display.set_mode((900, 650))
    pygame.display.set_caption("Sokoban AI - Single Agent")
    Game(screen, map_paths).run()


if __name__ == "__main__":
    main()