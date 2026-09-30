import pygame
import time

# Colors
WALL_COLOR = (105, 105, 105)       # Xám (%)
BG_COLOR = (240, 240, 240)         # Nền (spaces)
BOX_COLOR = (205, 133, 63)         # Nâu sáng (B)
BOX_ON_TARGET_COLOR = (101, 67, 33)# Nâu đậm (C)
TARGET_COLOR = (255, 50, 50)       # Đỏ (D)
PLAYER_COLOR = (50, 50, 255)       # Xanh (A)
TEXT_COLOR = (0, 0, 0)

CELL_SIZE = 40

class GameScreen:
    def __init__(self, screen, map_path, actions):
        self.screen = screen
        self.map_path = map_path
        self.actions = actions
        
        self.walls, self.targets, self.initial_boxes, self.initial_player = self.parse_map(map_path)
        self.states = self.generate_states(self.initial_player, self.initial_boxes, actions)
        
        self.current_step = 0
        self.is_playing = False
        self.last_update_time = time.time()
        self.play_speed = 0.3  # Thời gian mỗi bước khi auto-play (giây)
        
        self.font = pygame.font.SysFont("arial", 30)

    def parse_map(self, path):
        walls = set()
        targets = set()
        boxes = set()
        player = None
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for y, line in enumerate(lines):
            line = line.rstrip('\n')
            for x, char in enumerate(line):
                if char == '%':
                    walls.add((x, y))
                elif char == 'D':
                    targets.add((x, y))
                elif char == 'B':
                    boxes.add((x, y))
                elif char == 'C':
                    targets.add((x, y))
                    boxes.add((x, y))
                elif char == 'A':
                    player = (x, y)
        
        return walls, targets, boxes, player

    def generate_states(self, initial_player, initial_boxes, actions):
        """Mô phỏng lại quá trình di chuyển để tạo danh sách các trạng thái."""
        states = [(initial_player, set(initial_boxes))]
        
        curr_player = initial_player
        curr_boxes = set(initial_boxes)
        
        dir_map = {
            'North': (0, -1), 'N': (0, -1), 'U': (0, -1),
            'South': (0, 1), 'S': (0, 1), 'D': (0, 1),
            'West': (-1, 0), 'W': (-1, 0), 'L': (-1, 0),
            'East': (1, 0), 'E': (1, 0), 'R': (1, 0)
        }
        
        for action in actions:
            if action not in dir_map:
                continue
                
            dx, dy = dir_map[action]
            nx, ny = curr_player[0] + dx, curr_player[1] + dy
            
            if (nx, ny) in self.walls:
                states.append((curr_player, set(curr_boxes)))
                continue
                
            if (nx, ny) in curr_boxes:
                nnx, nny = nx + dx, ny + dy
                if (nnx, nny) not in self.walls and (nnx, nny) not in curr_boxes:
                    # Đẩy được box
                    curr_boxes.remove((nx, ny))
                    curr_boxes.add((nnx, nny))
                    curr_player = (nx, ny)
            else:
                # Di chuyển bình thường
                curr_player = (nx, ny)
                
            states.append((curr_player, set(curr_boxes)))
            
        return states

    def handle_event(self, event):
        """Xử lý phím Space, Left, Right và Escape."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "BACK_TO_MENU"
            elif event.key == pygame.K_SPACE:
                self.is_playing = not self.is_playing
            elif event.key == pygame.K_RIGHT:
                self.is_playing = False
                if self.current_step < len(self.states) - 1:
                    self.current_step += 1
            elif event.key == pygame.K_LEFT:
                self.is_playing = False
                if self.current_step > 0:
                    self.current_step -= 1
        return None

    def update(self):
        """Cập nhật trạng thái nếu đang auto-play."""
        if self.is_playing:
            now = time.time()
            if now - self.last_update_time > self.play_speed:
                if self.current_step < len(self.states) - 1:
                    self.current_step += 1
                    self.last_update_time = now
                else:
                    self.is_playing = False

    def draw(self):
        self.screen.fill(BG_COLOR)
        
        player_pos, boxes_pos = self.states[self.current_step]
        
        # Tính toán offset để vẽ map ra giữa màn hình (tùy chọn, ở đây vẽ từ góc)
        offset_x, offset_y = 50, 100
        
        # Vẽ tường
        for wx, wy in self.walls:
            pygame.draw.rect(self.screen, WALL_COLOR, 
                             (offset_x + wx * CELL_SIZE, offset_y + wy * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            
        # Vẽ điểm đích (D)
        for tx, ty in self.targets:
            pygame.draw.circle(self.screen, TARGET_COLOR, 
                               (offset_x + tx * CELL_SIZE + CELL_SIZE//2, offset_y + ty * CELL_SIZE + CELL_SIZE//2), 
                               CELL_SIZE//4)
                               
        # Vẽ boxes (B, C)
        for bx, by in boxes_pos:
            color = BOX_ON_TARGET_COLOR if (bx, by) in self.targets else BOX_COLOR
            pygame.draw.rect(self.screen, color, 
                             (offset_x + bx * CELL_SIZE + 2, offset_y + by * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4))
            
        # Vẽ người chơi (A)
        px, py = player_pos
        pygame.draw.circle(self.screen, PLAYER_COLOR, 
                           (offset_x + px * CELL_SIZE + CELL_SIZE//2, offset_y + py * CELL_SIZE + CELL_SIZE//2), 
                           CELL_SIZE//2 - 4)

        # UI thông tin
        # Yêu cầu: Display the number of actions on the UI
        info_text = f"Step: {self.current_step} / {len(self.actions)} | Action: "
        if self.current_step > 0 and self.current_step <= len(self.actions):
            info_text += self.actions[self.current_step - 1]
        else:
            info_text += "None"
            
        status_text = "PLAYING" if self.is_playing else "PAUSED"
        
        ui_surf1 = self.font.render(info_text, True, TEXT_COLOR)
        ui_surf2 = self.font.render(f"Trạng thái: {status_text} (Space: Play/Pause | Left/Right: Step | Esc: Back)", True, TEXT_COLOR)
        
        self.screen.blit(ui_surf1, (20, 20))
        self.screen.blit(ui_surf2, (20, 60))
