import heapq
from core.rules import Rules

def reconstruct_path(goal_state, parent):
    # Giữ nguyên hàm dò đường đi ngược
    path = []
    current_state = goal_state

    while current_state in parent:
        previous_state, action = parent[current_state]
        path.append(action)
        current_state = previous_state
        
    path.reverse()
    return path

def ucs(start_state, board):
    # UCS dùng priority queue (hàng đợi ưu tiên)
    # Sắp xếp các phần tử có phí nhỏ nhất ra trước
    priority_queue = []
    tie_breaker = 0 # Đếm thứ tự thêm vào để xử lý khi 2 state có cùng chi phí

    # Khởi tạo các biến thống kê bên NGOÀI vòng lặp
    expanded_nodes = 0
    max_queue_size = 1 

    heapq.heappush(priority_queue, (0, tie_breaker, start_state))

    visited = set() # Lưu các state đã CHỐT chi phí thấp nhất
    parent = {}     # Ghi nhớ đường đi
    cost_so_far = {start_state: 0} # Lưu chi phí tốt nhất của từng state

    while priority_queue:
        # Lấy ra trạng thái có phí rẻ nhất hiện tại
        current_fee, _, current_state = heapq.heappop(priority_queue)

        # Nếu trạng thái này đã được chốt (visited) trước đó với giá rẻ hơn thì bỏ qua
        if current_state in visited:
            continue
        
        # Đánh dấu trạng thái này đã được mở rộng và duyệt
        visited.add(current_state)
        expanded_nodes += 1 # Tăng số lượng node đã mở rộng

        # KHI TÌM THẤY ĐÍCH
        if current_state.is_goal(board):
            path = reconstruct_path(current_state, parent)
            # Trả về đủ 4 thông số
            return path, current_fee, expanded_nodes, max_queue_size

        # Lấy các bước đi tiếp theo
        successors = Rules.get_successors(current_state, board)

        for action, new_state in successors:
            new_cost = current_fee + 1 # Mỗi bước đi trong Sokoban tốn 1 chi phí

            # Chỉ đưa vào hàng đợi nếu:
            # 1. Chưa từng đi qua (not in visited)
            # 2. Hoặc tìm được một đường đi mới tới state này RẺ HƠN đường cũ
            if new_state not in visited and (new_state not in cost_so_far or new_cost < cost_so_far[new_state]):
                cost_so_far[new_state] = new_cost
                parent[new_state] = (current_state, action)
                
                tie_breaker += 1
                heapq.heappush(priority_queue, (new_cost, tie_breaker, new_state))
        
        # Cập nhật kích thước lớn nhất của hàng đợi (đo lường bộ nhớ)
        max_queue_size = max(max_queue_size, len(priority_queue))
                
    # Nếu hàng đợi rỗng mà không tìm thấy đích (No solution)
    return None, 0, expanded_nodes, max_queue_size