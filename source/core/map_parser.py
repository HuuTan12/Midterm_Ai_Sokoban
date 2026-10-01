#đọc file example_map.txt để lấy thông tin về wall,goal, hộp và vị trí của agent

from core.board import Board
from core.state import State

class MapParser:
    @staticmethod
    def load_map(file_path):
        #chịu trách nhiệm giao tiếp với hệ thống để đọc file
        with open(file_path,"r",encoding="utf-8") as file:
            #đọc từng dòng bỏ dấu xg dòng
            return [line.rstrip("\n") for line in file]
    @staticmethod
    def parse_level(map_lines):
        #xử lí mảng 2D
        walls = set()
        goals = set()
        boxes = []
        #chưa biết ở đâu thì none
        agent_box = None
        height = len(map_lines)
        #chặn lỗi văng game khi file map trống
        width = max((len(lines) for lines in map_lines),default = 0)

        #duyệt từng ô, col= vị trí cột, cell = kí tự
        for row,line in enumerate(map_lines):
            for col,cell in enumerate(line):
                pos = (row,col)
                if cell == "%":
                    walls.add(pos)
                elif cell == "D":
                    goals.add(pos)
                elif cell == "A":
                    agent_pos = pos
                elif cell == "B":
                    boxes.append(pos)
                elif cell == "C":
                    boxes.append(pos)
                    goals.add(pos)
        #đóng gói đưa về state để xử lí     
        board = Board(width =width,height = height,walls = walls,goals=goals)
        state = State(agent_pos = agent_pos,boxes = boxes)
        return board,state

    @staticmethod
    def parse_competitive_level(map_lines):
        from core.competitive_state import CompetitiveState
        walls = set()
        goals = set()
        boxes = []
        agent1_pos = None
        agent2_pos = None
        height = len(map_lines)
        width = max((len(lines) for lines in map_lines), default=0)

        for row, line in enumerate(map_lines):
            for col, cell in enumerate(line):
                pos = (row, col)
                if cell == "%":
                    walls.add(pos)
                elif cell == "D":
                    goals.add(pos)
                elif cell == "A":
                    agent1_pos = pos
                elif cell == "E":
                    agent2_pos = pos
                elif cell == "B":
                    boxes.append(pos)
                elif cell == "C":
                    boxes.append(pos)
                    goals.add(pos)
                    
        board = Board(width=width, height=height, walls=walls, goals=goals)
        state = CompetitiveState(agent1_pos, agent2_pos, boxes, [], [])
        return board, state

