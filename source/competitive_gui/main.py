import pygame
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from source.gui.menu import MenuScreen
from source.competitive_gui.game import CompetitiveGameScreen

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
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Sokoban Competitive - Nhóm Hieu")
    
    clock = pygame.time.Clock()
    
    map_paths = []
    maps_dir = os.path.join("source", "maps")
    if os.path.exists(maps_dir):
        for f in os.listdir(maps_dir):
            if f.endswith(".txt"):
                map_paths.append(os.path.join(maps_dir, f))
    
    current_state = "MENU"
    menu_screen = MenuScreen(screen, map_paths)
    game_screen = None
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if current_state == "MENU":
                if menu_screen.handle_event(event):
                    selected_map, selected_algo = menu_screen.get_selection()
                    
                    # Thuật toán chạy ngầm trong background với giới hạn n_steps
                    actions1, actions2 = real_competitive_search(selected_map, selected_algo, n_steps)
                    
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