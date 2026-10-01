import pygame
import os

class MenuScreen:
    def __init__(self, screen, map_paths):
        self.screen = screen
        self.map_paths = map_paths
        self.selected_map_index = 0
        self.algorithms = ["ucs", "astar"]
        self.selected_algo_index = 0
        self.font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 50)
        self.is_confirmed = False

    def handle_event(self, event):
        """Phím lên/xuống đổi map, trái/phải đổi thuật toán, Enter xác nhận."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_map_index = (self.selected_map_index - 1) % len(self.map_paths)
            elif event.key == pygame.K_DOWN:
                self.selected_map_index = (self.selected_map_index + 1) % len(self.map_paths)
            elif event.key == pygame.K_LEFT:
                self.selected_algo_index = (self.selected_algo_index - 1) % len(self.algorithms)
            elif event.key == pygame.K_RIGHT:
                self.selected_algo_index = (self.selected_algo_index + 1) % len(self.algorithms)
            elif event.key == pygame.K_RETURN:
                self.is_confirmed = True
                return True
        return False

    def draw(self):
        """Vẽ danh sách map, thuật toán đang chọn, hướng dẫn phím."""
        self.screen.fill((30, 30, 30))  # Nền tối

        # Vẽ tiêu đề
        title_surf = self.title_font.render("SOKOBAN - CHON MAP & THUAT TOAN", True, (255, 255, 255))
        self.screen.blit(title_surf, (50, 30))

        # Hướng dẫn
        guide_surf = self.font.render("Dung phim Len/Xuong de chon Map, Trai/Phai de chon Thuat toan. Nhan Enter", True, (150, 150, 150))
        self.screen.blit(guide_surf, (50, 80))

        # Vẽ danh sách Map
        y_offset = 150
        map_title = self.font.render("BAN DO (MAPS):", True, (200, 200, 255))
        self.screen.blit(map_title, (50, y_offset - 40))

        for i, map_path in enumerate(self.map_paths):
            map_name = os.path.basename(map_path)
            color = (0, 255, 0) if i == self.selected_map_index else (255, 255, 255)
            text_surf = self.font.render(f"{'> ' if i == self.selected_map_index else '  '}{map_name}", True, color)
            self.screen.blit(text_surf, (50, y_offset + i * 40))

        # Vẽ lựa chọn thuật toán
        y_algo_offset = y_offset + len(self.map_paths) * 40 + 40
        algo_title = self.font.render("THUAT TOAN:", True, (200, 200, 255))
        self.screen.blit(algo_title, (50, y_algo_offset))

        algo_text = f"<  {self.algorithms[self.selected_algo_index].upper()}  >"
        algo_surf = self.font.render(algo_text, True, (255, 255, 0))
        self.screen.blit(algo_surf, (250, y_algo_offset))

    def get_selection(self):
        """Trả về tuple(map_path, algorithm) đã chọn."""
        return self.map_paths[self.selected_map_index], self.algorithms[self.selected_algo_index]