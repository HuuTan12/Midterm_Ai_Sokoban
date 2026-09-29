import pygame
import time

# Colors
WALL_COLOR = (105, 105, 105)       # Xám (%)
BG_COLOR = (240, 240, 240)         # Nền (spaces)
TARGET_COLOR = (255, 50, 50)       # Đỏ (D)

# Colors for Agent 1
PLAYER1_COLOR = (50, 50, 255)       # Xanh dương
BOX1_COLOR = (100, 100, 255)        # Hộp của P1 chưa vào đích
BOX1_ON_TARGET_COLOR = (0, 0, 150)  # Hộp của P1 đã vào đích

# Colors for Agent 2
PLAYER2_COLOR = (50, 255, 50)       # Xanh lá
BOX2_COLOR = (100, 255, 100)        # Hộp của P2 chưa vào đích
BOX2_ON_TARGET_COLOR = (0, 150, 0)  # Hộp của P2 đã vào đích

NEUTRAL_BOX_COLOR = (205, 133, 63)  # Hộp trung lập chưa ai chạm vào

TEXT_COLOR = (0, 0, 0)

CELL_SIZE = 40

class CompetitiveGameScreen:
    def __init__(self, screen, map_path, actions1, actions2):
        self.screen = screen
        self.map_path = map_path
        self.actions1 = actions1
        self.actions2 = actions2
        
        self.walls, self.targets, self.initial_boxes, self.initial_p1, self.initial_p2 = self.parse_map(map_path)
        self.states = self.generate_states(self.initial_p1, self.initial_p2, self.initial_boxes, actions1, actions2)
        
        self.current_step = 0
        self.is_playing = False
        self.last_update_time = time.time()
        self.play_speed = 0.3  # Thời gian mỗi bước khi auto-play (giây)
        
        self.font = pygame.font.SysFont(None, 30)

    def parse_map(self, path):
        walls = set()
        targets = set()
        boxes = {} # dict lưu tọa độ hộp và ai đang sở hữu (0: trung lập, 1: P1, 2: P2)
        p1 = None
        p2 = None
        
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
                    boxes[(x, y)] = 0
                elif char == 'C':
                    targets.add((x, y))
                    boxes[(x, y)] = 0
                elif char == '1': # Giả sử '1' là Agent 1 (nếu có map đặc chế)
                    p1 = (x, y)
                elif char == '2': # Giả sử '2' là Agent 2 (nếu có map đặc chế)
                    p2 = (x, y)
                elif char == 'A': # Nếu dùng chung ký tự A, cứ gán tạm
                    if p1 is None:
                        p1 = (x, y)
                    else:
                        p2 = (x, y)
                        
        if p2 is None:
            # Fallback nếu map không có agent 2
            p2 = (0, 0)
            
        return walls, targets, boxes, p1, p2

    def generate_states(self, initial_p1, initial_p2, initial_boxes, actions1, actions2):
        """Mô phỏng lại quá trình di chuyển của 2 agents đồng thời."""
        states = [(initial_p1, initial_p2, dict(initial_boxes))]
        
        curr_p1 = initial_p1
        curr_p2 = initial_p2
        curr_boxes = dict(initial_boxes)
        
        dir_map = {
            'North': (0, -1), 'N': (0, -1), 'U': (0, -1),
            'South': (0, 1), 'S': (0, 1), 'D': (0, 1),
            'West': (-1, 0), 'W': (-1, 0), 'L': (-1, 0),
            'East': (1, 0), 'E': (1, 0), 'R': (1, 0)
        }
        
        max_steps = max(len(actions1), len(actions2))
        
        for i in range(max_steps):
            a1 = actions1[i] if i < len(actions1) else None
            a2 = actions2[i] if i < len(actions2) else None
            
            # Logic mô phỏng ở đây cần phức tạp hơn (xử lý va chạm giữa 2 agents)
            # Tạm thời thực hiện tuần tự P1 rồi tới P2 cho đơn giản
            
            # Agent 1
            if a1 and a1 in dir_map:
                dx, dy = dir_map[a1]
                nx, ny = curr_p1[0] + dx, curr_p1[1] + dy
                
                if (nx, ny) not in self.walls and (nx, ny) != curr_p2:
                    if (nx, ny) in curr_boxes:
                        nnx, nny = nx + dx, ny + dy
                        if (nnx, nny) not in self.walls and (nnx, nny) not in curr_boxes and (nnx, nny) != curr_p2:
                            owner = curr_boxes.pop((nx, ny))
                            curr_boxes[(nnx, nny)] = 1 # Đánh dấu hộp thuộc P1
                            curr_p1 = (nx, ny)
                    else:
                        curr_p1 = (nx, ny)
                        
            # Agent 2
            if a2 and a2 in dir_map:
                dx, dy = dir_map[a2]
                nx, ny = curr_p2[0] + dx, curr_p2[1] + dy
                
                if (nx, ny) not in self.walls and (nx, ny) != curr_p1:
                    if (nx, ny) in curr_boxes:
                        nnx, nny = nx + dx, ny + dy
                        if (nnx, nny) not in self.walls and (nnx, nny) not in curr_boxes and (nnx, nny) != curr_p1:
                            owner = curr_boxes.pop((nx, ny))
                            curr_boxes[(nnx, nny)] = 2 # Đánh dấu hộp thuộc P2
                            curr_p2 = (nx, ny)
                    else:
                        curr_p2 = (nx, ny)
                        
            states.append((curr_p1, curr_p2, dict(curr_boxes)))
            
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
        
        p1_pos, p2_pos, boxes_dict = self.states[self.current_step]
        
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
                               
        # Vẽ boxes 
        for (bx, by), owner in boxes_dict.items():
            if owner == 1:
                color = BOX1_ON_TARGET_COLOR if (bx, by) in self.targets else BOX1_COLOR
            elif owner == 2:
                color = BOX2_ON_TARGET_COLOR if (bx, by) in self.targets else BOX2_COLOR
            else:
                color = NEUTRAL_BOX_COLOR
                
            pygame.draw.rect(self.screen, color, 
                             (offset_x + bx * CELL_SIZE + 2, offset_y + by * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4))
            
        # Vẽ người chơi
        px, py = p1_pos
        pygame.draw.circle(self.screen, PLAYER1_COLOR, 
                           (offset_x + px * CELL_SIZE + CELL_SIZE//2, offset_y + py * CELL_SIZE + CELL_SIZE//2), 
                           CELL_SIZE//2 - 4)
                           
        px2, py2 = p2_pos
        pygame.draw.circle(self.screen, PLAYER2_COLOR, 
                           (offset_x + px2 * CELL_SIZE + CELL_SIZE//2, offset_y + py2 * CELL_SIZE + CELL_SIZE//2), 
                           CELL_SIZE//2 - 4)

        # UI thông tin
        total_steps = len(self.states) - 1
        info_text = f"Step: {self.current_step} / {total_steps}"
            
        status_text = "PLAYING" if self.is_playing else "PAUSED"
        
        ui_surf1 = self.font.render(info_text, True, TEXT_COLOR)
        ui_surf2 = self.font.render(f"Trạng thái: {status_text} (Space: Play/Pause | Left/Right: Step | Esc: Back)", True, TEXT_COLOR)
        
        self.screen.blit(ui_surf1, (20, 20))
        self.screen.blit(ui_surf2, (20, 60))
