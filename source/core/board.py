#lưu cấu trúc cố định của wall,goal, kích thước

class Board:
    #__init___ khởi tạo board với width, height, wall, goal,
    def __init__(self, width, height, walls, goals):
        self.width = width
        self.height = height
        self.walls = frozenset(walls)
        self.goals = frozenset(goals)
        
    #kiểm tra tọa độ có đụng tường không
    def is_wall(self, position):
        return position in self.walls
    
    #kiểm tra tọa độ có phải goal không
    def is_goal(self, position):
        return position in self.goals   
    
    #kiểm tra tọa độ có nằm ngoài board không
    def is_within_bounds(self, position):
        row, col = position
        return 0 <= row < self.height and 0 <= col < self.width 
    
        