import pygame
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from source.gui.menu import MenuScreen
from source.competitive_gui.game import CompetitiveGameScreen

def dummy_competitive_search(map_path, algorithm):
    """
    Hàm giả lập trả về danh sách các hành động của 2 agents.
    """
    actions_p1 = ["East", "East", "South", "West", "North"]
    actions_p2 = ["West", "West", "North", "East", "South"]
    return actions_p1, actions_p2

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Sokoban Competitive - Nhóm Hieu")
    
    clock = pygame.time.Clock()
    
    sample_map = "example_map_competitive.txt"
    if not os.path.exists(sample_map):
        with open(sample_map, "w", encoding="utf-8") as f:
            f.write(" %%%%%\n")
            f.write("%%% %\n")
            f.write("%D1B %\n")
            f.write("%%% BD%\n")
            f.write("%D%%B %\n")
            f.write("% % D %%\n")
            f.write("%B 2BBD%\n")
            f.write("% D %\n")
            f.write("%%%%%%%%\n")
            
    map_paths = [sample_map]
    
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
                    
                    actions1, actions2 = dummy_competitive_search(selected_map, selected_algo)
                    
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
