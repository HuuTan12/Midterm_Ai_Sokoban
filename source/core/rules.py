# kiểm tra di chuyển, đẩy box, thắng ,thua
from core.action import Action
from core.state import State

class Rules:
    # bản đồ vectow hướng đi
    #row là lên/xuống, col là trái/phải.    
    Directions = {
        Action.NORTH : (-1,0),  #di chuyển lên trên
        Action.SOUTH: (1, 0),  #di chuyển xuống dưới
        Action.WEST: (0, -1),  #di chuyển sang trái
        Action.EAST: (0, 1)   #di chuyển sang phải
    }

    @staticmethod
    #hàm tính toán các trạng thái có thể di chuyển tới từ trạng thái hiện tại   
    def get_successors(state,board):
        #tạo danh sách các hành động có thể thực hiện   
        successors = []

        #lấy vị trí của agent
        row, col = state.agent_pos

        #thử cả 4 hướng đi
        for action,(drow,dcol) in Rules.Directions.items():

            #tính vị  trí của agent
            new_row = row + drow
            new_col = col + dcol
            new_agent_pos = (new_row,new_col)

            #nếu ngoài map hoặc đụng wall -> đi không được thì xử lí
            if (not board.is_within_bounds(new_agent_pos) or board.is_wall(new_agent_pos)):
                continue
            
            #nếu vị trí có box thì đẩy box và không thể đi xuyên qua 
            if new_agent_pos in state.boxes:
                #tính vị trí của box sau khi đẩy
                box_new_row = new_row + drow
                box_new_col = new_col + dcol
                box_new_pos = (box_new_row,box_new_col) 
                
                #nếu box không thể đẩy -> đi không được thì xử lí
                if (not board.is_within_bounds(box_new_pos) or 
                board.is_wall(box_new_pos) or box_new_pos in state.boxes):
                    continue
                
                #tạo ds box mới
                new_boxes = list(state.boxes)

                #box cũ ở vị trí new_agent_pos
                new_boxes.remove(new_agent_pos)
                new_boxes.append(box_new_pos)

                #tạo state mới
                successors.append((action.value,State(new_agent_pos,new_boxes)))

            #nếu vị trí đó không có box thì chỉ đơn giản di chuyển agent
            else:
                #tạo state mới
                successors.append((action.value,State(new_agent_pos,state.boxes)))  
        
        return successors   
           

    