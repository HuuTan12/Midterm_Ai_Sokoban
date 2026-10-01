
import pygame
import sys
import os

# Thêm đường dẫn để có thể import các module khác (nếu cần thiết sau này)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gui.menu import MenuScreen
from gui.game import GameScreen
from core.map_parser import MapParser
from search.ucs import UCS
from search.astar import AStar

def real_search(map_path, algorithm):
    print(f"Đang chạy thuật toán {algorithm} cho {map_path}...")
    map_lines = MapParser.load_map(map_path)
    board, start_state = MapParser.parse_level(map_lines)
    
    if algorithm == "ucs":
        path, _, _, _ = UCS().search(start_state, board)
    elif algorithm == "astar":
        path, _, _, _ = AStar().search(start_state, board)
    else:
        path = []
        
    return path if path else []

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Sokoban AI - Nhóm Tan - Hieu")
    
    clock = pygame.time.Clock()
    
    map_paths = []
    # Lấy các map khác trong thư mục source/maps nếu có
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
                    # Người dùng đã chọn xong map và thuật toán
                    selected_map, selected_algo = menu_screen.get_selection()
                    
                    # Chạy thuật toán tìm kiếm thật
                    actions = real_search(selected_map, selected_algo)
                    
                    # Chuyển sang màn hình game
                    game_screen = GameScreen(screen, selected_map, actions)
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
