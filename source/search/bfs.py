#BFS dùng Queue (hàng đợi).
#Nguyên tắc:
#Vào trước → ra trước (FIFO: First In, First Out)

from collections import deque
from core.rules import Rules

def reconstruct_path(goal_state, parent):
    #khởi tạo đường đi path
    path = []
    current_state = goal_state

    while current_state in parent:
        previous_state, action = parent[current_state]

        path.append(action)

        current_state = previous_state

    path.reverse()

    return path

def bfs(start_state,board):
    queue = deque()
    #lưu state đã gặp để tránh lặp
    visited = set()
    #nhớ vị trí
    parent={}

    queue.append(start_state)
    visited.add(start_state)

    
    while queue:
        #popleft là lấy phần tử đầu
        current_state = queue.popleft()
        if current_state.is_goal(board):
            path = reconstruct_path(current_state, parent)
            return path
        successors = Rules.get_successors(current_state,board)

        for action,new_state in successors:
            if new_state in visited:
                continue

            visited.add(new_state)
            parent[new_state] = (current_state,action)
            queue.append(new_state)

    return None