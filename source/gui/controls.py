from enum import Enum
import pygame

class Command(Enum):
    TOGGLE_PAUSE  = "toggle_pause"
    STEP_FORWARD  = "step_forward"
    STEP_BACKWARD = "step_backward"
    JUMP_TO_START = "jump_to_start"
    JUMP_TO_END   = "jump_to_end"
    QUIT          = "quit"
    BACK_TO_MENU  = "back_to_menu"

def map_event_to_command(event):
    if event.type == pygame.QUIT:
        return Command.QUIT
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            return Command.TOGGLE_PAUSE
        elif event.key == pygame.K_RIGHT:
            if event.mod & pygame.KMOD_SHIFT:
                return Command.JUMP_TO_END
            return Command.STEP_FORWARD
        elif event.key == pygame.K_LEFT:
            if event.mod & pygame.KMOD_SHIFT:
                return Command.JUMP_TO_START
            return Command.STEP_BACKWARD
        elif event.key == pygame.K_HOME:
            return Command.JUMP_TO_START
        elif event.key == pygame.K_END:
            return Command.JUMP_TO_END
        elif event.key == pygame.K_ESCAPE:
            return Command.BACK_TO_MENU
        elif event.key == pygame.K_q and (event.mod & pygame.KMOD_CTRL):
            return Command.QUIT
    return None
