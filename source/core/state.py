# lưu lại trạng thái của player với boxes...
## Lưu trạng thái thay đổi của game

class State:
    def __init__(self,agent_pos, boxes):
        #agent_pos là một tuple(row,col) 
        self.agent_pos = agent_pos
        #boxes là một frozenset các tuple(row,col)
        self.boxes = tuple(sorted(boxes))  #sắp xếp các box để đảm bảo tính duy nhất

    def __eq__(self, other):
        #so sánh hai trạng thái có giống nhau không
        if not isinstance(other,State):
            return False
        return self.agent_pos == other.agent_pos and self.boxes == other.boxes
    
    def __hash__(self):
        #tạo mã băm duy nhất dựa trên tọa độ nhân vật và các hộp
        #giúp tìm kiếm trạng thái nhanh hơn 
        return hash((self.agent_pos,self.boxes))

    def is_goal(self,board):
        
        #Sử dụng hàm is_goal từ class Board bạn vừa tạo để kiểm tra chiến thắng.
        #Trạng thái đích là khi toàn bộ hộp đều nằm trên ô goal.
        
        for box in self.boxes:
            if not board.is_goal(box):
                return False
        return True