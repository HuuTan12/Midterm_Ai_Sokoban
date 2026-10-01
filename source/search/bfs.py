# BFS - Breadth-First Search
# Nguyên tắc:
#   - Dùng Queue (hàng đợi FIFO: First In, First Out)
#   - Đảm bảo tìm đường ngắn nhất theo số bước
#   - Không cần heuristic

from collections import deque
from core.rules import Rules
from search.search_algorithm import SearchAlgorithm


def _reconstruct_path(goal_state, parent):
    """Truy vết đường đi từ trạng thái đích về trạng thái ban đầu."""
    path = []
    current_state = goal_state
    while current_state in parent:
        previous_state, action = parent[current_state]
        path.append(action)
        current_state = previous_state
    path.reverse()
    return path


class BFS(SearchAlgorithm):
    """
    Breadth-First Search cho bài toán Sokoban.

    Đặc điểm:
      - Duyệt theo chiều rộng, đảm bảo tìm đường ngắn nhất (ít bước nhất).
      - Không dùng heuristic.
      - Tốn bộ nhớ nhiều hơn UCS/A* với bản đồ lớn.

    Returns:
        (path, cost, expanded_nodes, max_queue_size)
        Trả về (None, 0, expanded_nodes, max_queue_size) nếu không tìm được.
    """

    def search(self, start_state, board, timeout_seconds=30.0):
        import time
        start_time = time.time()

        queue = deque()
        visited = set()
        parent = {}
        expanded_nodes = 0
        max_queue_size = 1

        queue.append(start_state)
        visited.add(start_state)

        while queue:
            # Kiểm tra timeout
            if time.time() - start_time > timeout_seconds:
                return None, 0, expanded_nodes, max_queue_size

            # Lấy phần tử đầu hàng đợi (FIFO)
            current_state = queue.popleft()
            expanded_nodes += 1

            # Kiểm tra đích
            if current_state.is_goal(board):
                path = _reconstruct_path(current_state, parent)
                cost = len(path)
                return path, cost, expanded_nodes, max_queue_size

            # Mở rộng các trạng thái con
            successors = Rules.get_successors(current_state, board)
            for action, new_state in successors:
                if new_state in visited:
                    continue
                visited.add(new_state)
                parent[new_state] = (current_state, action)
                queue.append(new_state)

            max_queue_size = max(max_queue_size, len(queue))

        return None, 0, expanded_nodes, max_queue_size