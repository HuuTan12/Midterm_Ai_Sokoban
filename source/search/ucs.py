
import heapq

from core.rules import Rules

def reconstruct_path(goal_state,parent):
    #giữ nguyên hàm dò đường đi ngược của BFS
    path=[]
    current_state = goal_state

    while current_state in parent:
        previous_state,action = parent[current_state]

        path.append(action)

        current_state = previous_state
    path.reverse()
    return path

def ucs(start_state,board):
    #ucs dùng priority queue là hàng đợi ưu tiên
    #xắp sếp các phaafnm tử có phí nhỏ nhất ra trước
    priority_queue = []

    tie_breaker = 0 # đếm lần sập game khi 2 state gặp nhau

    heapq.heappush(priority_queue,(0,tie_breaker,start_state))

    visited = set() #lưu các state đã gặp
    parent = {} # ghi nhớ đường đi

    cost_so_far = {start_state:0} # lưu chi phí của từng staticmethod

    while priority_queue:
        #lấy ra trạng thái có phí rẻ nhất hiện tại

        current_fee,_,current_state = heapq.heappop(priority_queue)

        if current_state.is_goal(board):
           path = reconstruct_path(current_state, parent)
           return path, current_fee

        # Nếu trạng thái này đã được chốt (visited) trước đó với giá rẻ hơn thì bỏ qua
        if current_state in visited:
            continue
        
        visited.add(current_state)

        # Lấy các bước đi tiếp theo
        successors = Rules.get_successors(current_state, board)

        for action, new_state in successors:
            new_cost = current_fee + 1 # Mỗi bước đi tốn 1 chi phí

            # Chỉ đưa vào hàng đợi nếu:
            # 1. Chưa từng đi qua (not in visited)
            # 2. Hoặc tìm được một đường đi mới tới state này RẺ HƠN đường cũ
            if new_state not in visited and (new_state not in cost_so_far or new_cost < cost_so_far[new_state]):
                cost_so_far[new_state] = new_cost
                parent[new_state] = (current_state, action)
                
                tie_breaker += 1
                heapq.heappush(priority_queue, (new_cost, tie_breaker, new_state))
    return None

