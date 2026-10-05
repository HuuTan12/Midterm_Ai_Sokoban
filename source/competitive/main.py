import pygame
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC_DIR  = os.path.join(ROOT_DIR, 'source')
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, SRC_DIR)

from source.gui.menu import MenuScreen
from source.competitive.game import CompetitiveGameScreen


def is_competitive_map(map_path):
    try:
        with open(map_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return 'A' in content and 'E' in content
    except Exception:
        return False


def real_competitive_search(map_path, algorithm, n_steps=200):
    from source.core.map_parser import MapParser
    from source.core.competitive_rules import CompetitiveRules
    from source.search.agent_tan import AgentTan
    from source.search.agent_hieu import AgentHieu

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
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Sokoban Competitive - Hieu's Team")

    clock = pygame.time.Clock()

    map_paths = []
    maps_dir = os.path.join(ROOT_DIR, "source", "maps")
    if os.path.exists(maps_dir):
        for f in sorted(os.listdir(maps_dir)):
            if f.endswith(".txt"):
                full_path = os.path.join(maps_dir, f)
                if is_competitive_map(full_path):
                    map_paths.append(full_path)

    if not map_paths:
        print("[ERROR] No competitive maps found in source/maps/")
        print("        Competitive maps need 'A' (agent 1) and 'E' (agent 2).")
        pygame.quit()
        return

    current_state = "MENU"
    menu_screen = MenuScreen(screen, map_paths, is_competitive=True)
    game_screen = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if current_state == "MENU":
                if menu_screen.handle_event(event):
                    selected_map, selected_algo, step_limit = menu_screen.get_selection()

                    actions1, actions2 = real_competitive_search(selected_map, selected_algo, step_limit)

                    game_screen = CompetitiveGameScreen(screen, selected_map, actions1, actions2)
                    current_state = "GAME"

            elif current_state == "GAME":
                action_result = game_screen.handle_event(event)
                if action_result == "BACK_TO_MENU":
                    current_state = "MENU"
                    menu_screen.is_confirmed = False

        if current_state == "MENU":
            menu_screen.draw()
        elif current_state == "GAME":
            game_screen.update()
            game_screen.draw()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()