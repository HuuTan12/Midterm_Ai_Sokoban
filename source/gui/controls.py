from enum import Enum
import pygame

class Command(Enum):
    """Ánh xạ phím bấm sang lệnh game - tách biệt logic điều khiển với logic game."""
    TOGGLE_PAUSE = "toggle_pause"    # Space
    STEP_FORWARD = "step_forward"    # Mũi tên Phải
    STEP_BACKWARD = "step_backward"  # Mũi tên Trái
    QUIT = "quit"                    # Ctrl+Q hoặc đóng cửa sổ
    BACK_TO_MENU = "back_to_menu"   # Escape

def map_event_to_command(event):
    """Nhận vào một pygame.event, trả về Command hoặc None nếu không liên quan."""
    if event.type == pygame.QUIT:
        return Command.QUIT
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            return Command.TOGGLE_PAUSE
        elif event.key == pygame.K_RIGHT:
            return Command.STEP_FORWARD
        elif event.key == pygame.K_LEFT:
            return Command.STEP_BACKWARD
        elif event.key == pygame.K_ESCAPE:
            return Command.BACK_TO_MENU
        elif event.key == pygame.K_q and (event.mod & pygame.KMOD_CTRL):
            return Command.QUIT
    return None
