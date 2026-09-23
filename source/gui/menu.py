import pygame

class MenuScreen:
    def __init__(self, screen, map_paths: list[str]):
        self.screen = screen
        self.map_paths = map_paths
        self.selected_map_index = 0
        self.selected_algorithm = "ucs"  # hoặc "astar"

    def handle_event(self, event):
        """Phím lên/xuống đổi map, trái/phải đổi thuật toán, Enter xác nhận."""
        # TODO
        # Trả về True nếu người dùng đã xác nhận (Enter)

    def draw(self):
        """Vẽ danh sách map, thuật toán đang chọn, hướng dẫn phím."""
        # TODO

    def get_selection(self) -> tuple[str, str]:
        """Trả (map_path, algorithm) đã chọn."""
        return self.map_paths[self.selected_map_index], self.selected_algorithm