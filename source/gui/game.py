import threading
import queue
import pygame
from renderer import Renderer
from menu import MenuScreen
from controls import map_event_to_command, Command
# from core.map_loader import load_map      # của Người 1
# from search import search                  # của Người 1

class AppState:
    MENU = "menu"
    SOLVING = "solving"
    PLAYING = "playing"
    FINISHED = "finished"
    NO_SOLUTION = "no_solution"

class Game:
    def __init__(self, map_paths: list[str]):
        pygame.init()
        self.screen = pygame.display.set_mode((900, 600))
        self.clock = pygame.time.Clock()
        self.state = AppState.MENU
        self.menu = MenuScreen(self.screen, map_paths)
        self.renderer = None
        self.states_history = []
        self.current_step = 0
        self.paused = True
        self.playback_speed_ms = 400
        self._last_tick = 0
        self.result_info = {}
        self._search_thread = None
        self._search_result_queue = queue.Queue()

    def start_solving(self):
        map_path, algorithm = self.menu.get_selection()
        # TODO: problem = load_map(map_path)
        # Chạy search ở luồng phụ để không đơ cửa sổ:
        def worker():
            # result = search(problem, algorithm)
            # self._search_result_queue.put((problem, result))
            pass
        self._search_thread = threading.Thread(target=worker, daemon=True)
        self._search_thread.start()
        self.state = AppState.SOLVING

    def poll_search_result(self):
        try:
            problem, result = self._search_result_queue.get_nowait()
        except queue.Empty:
            return
        if result.actions is None:
            self.state = AppState.NO_SOLUTION
            return
        # TODO: dựng self.states_history bằng cách áp lần lượt result.actions
        # lên problem.initial_state qua problem.result(state, action)
        self.renderer = Renderer(self.screen, problem.grid)
        self.current_step = 0
        self.paused = True
        self.result_info = {
            "algorithm": self.menu.get_selection()[1],
            "cost": result.cost,
            "expanded": result.expanded,
            "time_sec": result.time_sec,
            "total_steps": len(result.actions),
        }
        self.state = AppState.PLAYING

    def apply_command(self, cmd: Command):
        if cmd == Command.QUIT:
            pygame.quit(); raise SystemExit
        if self.state not in (AppState.PLAYING,):
            if cmd == Command.BACK_TO_MENU:
                self.state = AppState.MENU
            return
        if cmd == Command.TOGGLE_PAUSE:
            self.paused = not self.paused
        elif cmd == Command.STEP_FORWARD:
            self.paused = True
            self.current_step = min(self.current_step + 1, len(self.states_history) - 1)
        elif cmd == Command.STEP_BACKWARD:
            self.paused = True
            self.current_step = max(self.current_step - 1, 0)
        elif cmd == Command.RESTART:
            self.current_step = 0
        elif cmd == Command.SPEED_UP:
            self.playback_speed_ms = max(50, self.playback_speed_ms - 50)
        elif cmd == Command.SPEED_DOWN:
            self.playback_speed_ms += 50
        elif cmd == Command.BACK_TO_MENU:
            self.state = AppState.MENU

    def auto_advance(self, now_ms: int):
        if self.paused or self.current_step >= len(self.states_history) - 1:
            return
        if now_ms - self._last_tick >= self.playback_speed_ms:
            self.current_step += 1
            self._last_tick = now_ms

    def run(self):
        while True:
            now = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); return
                if self.state == AppState.MENU:
                    if self.menu.handle_event(event):
                        self.start_solving()
                else:
                    cmd = map_event_to_command(event)
                    if cmd:
                        self.apply_command(cmd)

            if self.state == AppState.SOLVING:
                self.poll_search_result()
            elif self.state == AppState.PLAYING:
                self.auto_advance(now)

            self._draw()
            self.clock.tick(60)

    def _draw(self):
        self.screen.fill((255, 255, 255))
        if self.state == AppState.MENU:
            self.menu.draw()
        elif self.state == AppState.SOLVING:
            # TODO: vẽ chữ "Đang tìm lời giải..."
            pass
        elif self.state == AppState.NO_SOLUTION:
            # TODO: vẽ thông báo vô nghiệm, hướng dẫn quay lại menu
            pass
        elif self.state in (AppState.PLAYING,):
            self.renderer.draw_static()
            self.renderer.draw_state(self.states_history[self.current_step])
            info = dict(self.result_info, step=self.current_step,
                        status="paused" if self.paused else "playing")
            self.renderer.draw_panel(info)
        pygame.display.flip()

if __name__ == "__main__":
    Game(map_paths=["../maps/single/t08_example.txt"]).run()