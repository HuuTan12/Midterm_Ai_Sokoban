import pygame
import sys
import os

# Thêm cả thư mục gốc VÀ thư mục source để import core, search đúng
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC_DIR  = os.path.join(ROOT_DIR, 'source')
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, SRC_DIR)

from source.gui.menu import MenuScreen
from source.competitive_gui.game import CompetitiveGameScreen
import threading


def is_competitive_map(map_path):
    """Kiểm tra map có đủ 2 agents không (phải có cả 'A' và 'E')."""
    try:
        with open(map_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return 'A' in content and 'E' in content
    except Exception:
        return False


def real_competitive_search(map_path, algorithm, n_steps=50):
    from core.map_parser import MapParser
    from core.competitive_rules import CompetitiveRules
    from search.agent_tan import AgentTan
    from search.agent_hieu import AgentHieu

    map_lines = MapParser.load_map(map_path)
    board, state = MapParser.parse_competitive_level(map_lines)

    agent1 = AgentTan()
    agent2 = AgentHieu()

    actions1 = []
    actions2 = []

    for i in range(n_steps):
        a1 = agent1.get_action(state, board)
        a2 = agent2.get_action(state, board)

        if a1 is None and a2 is None:
            break

        actions1.append(a1)
        actions2.append(a2)

        state = CompetitiveRules.apply_actions(state, a1, a2, board)

    return actions1, actions2


def main(n_steps=50):
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Sokoban Competitive - Nhom Hieu")

    clock = pygame.time.Clock()

    # === FIX: Chỉ load map HỢP LỆ cho competitive (có đủ 2 agents 'A' và 'E') ===
    map_paths = []
    maps_dir = os.path.join(ROOT_DIR, "source", "maps")
    if os.path.exists(maps_dir):
        for f in sorted(os.listdir(maps_dir)):
            if f.endswith(".txt"):
                full_path = os.path.join(maps_dir, f)
                if is_competitive_map(full_path):
                    map_paths.append(full_path)

    if not map_paths:
        print("[LOI] Khong tim thay map nao co 2 agents trong source/maps/")
        print("      Map competitive can co ky tu 'A' (agent 1) va 'E' (agent 2).")
        pygame.quit()
        return

    current_state = "MENU"
    menu_screen = MenuScreen(screen, map_paths)
    game_screen = None
    
    search_result = None
    search_lock = threading.Lock()
    selected_map = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if current_state == "MENU":
                if menu_screen.handle_event(event):
                    selected_map, selected_algo = menu_screen.get_selection()

                    def worker(m_path, algo, steps):
                        res = real_competitive_search(m_path, algo, steps)
                        with search_lock:
                            nonlocal search_result
                            search_result = res
                    
                    search_result = None
                    current_state = "SOLVING"
                    threading.Thread(target=worker, args=(selected_map, selected_algo, n_steps), daemon=True).start()

            elif current_state == "GAME":
                action_result = game_screen.handle_event(event)
                if action_result == "BACK_TO_MENU":
                    current_state = "MENU"
                    menu_screen.is_confirmed = False

        if current_state == "SOLVING":
            with search_lock:
                if search_result is not None:
                    actions1, actions2 = search_result
                    game_screen = CompetitiveGameScreen(screen, selected_map, actions1, actions2)
                    current_state = "GAME"

        if current_state == "MENU":
            menu_screen.draw()
        elif current_state == "SOLVING":
            screen.fill((30, 30, 30))
            font = pygame.font.SysFont("arial", 30)
            text = font.render("Dang tinh toan loi giai 2 agents... Vui long doi.", True, (255, 220, 0))
            sw, sh = screen.get_size()
            screen.blit(text, ((sw - text.get_width()) // 2, sh // 2 - 20))
        elif current_state == "GAME":
            game_screen.update()
            game_screen.draw()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()