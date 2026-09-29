import pygame
import sys
import os

# Thêm đường dẫn để có thể import các module khác (nếu cần thiết sau này)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from source.gui.menu import MenuScreen
from source.gui.game import GameScreen

def dummy_search(map_path, algorithm):
    """
    Hàm giả lập trả về danh sách các hành động để test GUI.
    Sau này nhóm của bạn (những người làm thuật toán) sẽ thay thế hàm này
    bằng hàm gọi UCS hoặc A* thật.
    """
    # Trả về một chuỗi hành động mẫu giả định
    print(f"Đang chạy thuật toán {algorithm} cho {map_path}...")
    return ["East", "East", "South", "West", "North", "East"]

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Sokoban AI - Nhóm Hieu")
    
    clock = pygame.time.Clock()
    
    # Tạo một file map mẫu để test nếu chưa có
    sample_map = "example_map.txt"
    if not os.path.exists(sample_map):
        with open(sample_map, "w", encoding="utf-8") as f:
            f.write(" %%%%%\n")
            f.write("%%% %\n")
            f.write("%DAB %\n")
            f.write("%%% BD%\n")
            f.write("%D%%B %\n")
            f.write("% % D %%\n")
            f.write("%B CBBD%\n")
            f.write("% D %\n")
            f.write("%%%%%%%%\n")
            
    map_paths = [sample_map]
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
                    
                    # Chạy thuật toán tìm kiếm (gọi dummy ở đây, thay thế bằng thuật toán thật sau)
                    actions = dummy_search(selected_map, selected_algo)
                    
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
