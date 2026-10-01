# GBFS - Greedy Best-First Search
# Nguyên tắc:
#   - Dùng Priority Queue, ưu tiên theo f(n) = h(n) (chỉ heuristic)
#   - Không quan tâm chi phí đã đi g(n)
#   - Thường nhanh hơn A*, nhưng KHÔNG đảm bảo tối ưu
#
# So sánh:
#   A*   : f = g + h  →  tối ưu + đầy đủ
#   GBFS : f = h      →  nhanh, nhưng có thể không tối ưu

import heapq
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


def _chebyshev_distance(pos1, pos2):
    """Khoảng cách Chebyshev giữa hai điểm (cho phép di chuyển 8 hướng)."""
    row1, col1 = pos1
    row2, col2 = pos2
    return max(abs(row1 - row2), abs(col1 - col2))


class GBFS(SearchAlgorithm):
    """
    Greedy Best-First Search cho bài toán Sokoban.

    Heuristic: Tổng khoảng cách Chebyshev từ mỗi box đến goal gần nhất chưa có box.
    Hàm ưu tiên: f(n) = h(n)  (greedy - tham lam)

    Đặc điểm:
      - Thường mở rộng ít node hơn A*, chạy nhanh hơn.
      - Không đảm bảo đường đi tối ưu (ít bước nhất).
      - Có thể bị kẹt trong vòng lặp nếu không có visited set.

    Returns:
        (path, cost, expanded_nodes, max_queue_size)
        Trả về (None, 0, expanded_nodes, max_queue_size) nếu không tìm được.
    """

    def heuristic(self, state, board):
        """
        Tính h(n): tổng khoảng cách Chebyshev từ mỗi box chưa ở goal
        đến goal gần nhất còn trống.
        """
        misplaced_boxes  = list(set(state.boxes) - board.goals)
        available_goals  = list(board.goals - set(state.boxes))

        if not misplaced_boxes:
            return 0

        total = 0
        for box in misplaced_boxes:
            best_dist = float("inf")
            for goal in available_goals:
                dist = _chebyshev_distance(box, goal)
                if dist < best_dist:
                    best_dist = dist
            total += best_dist
        return total

    def search(self, start_state, board, timeout_seconds=30.0):
        import time
        start_time  = time.time()
        pq          = []
        tie_breaker = 0
        expanded_nodes  = 0
        max_queue_size  = 1

        h_start = self.heuristic(start_state, board)
        heapq.heappush(pq, (h_start, tie_breaker, start_state))

        visited = set()
        parent  = {}
        # Theo dõi chi phí thực tế (số bước) để báo cáo
        g_score = {start_state: 0}

        while pq:
            # Kiểm tra timeout
            if time.time() - start_time > timeout_seconds:
                return None, 0, expanded_nodes, max_queue_size

            current_h, _, current_state = heapq.heappop(pq)

            # Bỏ qua nếu đã thăm
            if current_state in visited:
                continue

            visited.add(current_state)
            expanded_nodes += 1

            # Kiểm tra đích
            if current_state.is_goal(board):
                path = _reconstruct_path(current_state, parent)
                cost = g_score.get(current_state, len(path))
                return path, cost, expanded_nodes, max_queue_size

            # Mở rộng các trạng thái con
            successors = Rules.get_successors(current_state, board)
            for action, new_state in successors:
                if new_state in visited:
                    continue

                new_g = g_score.get(current_state, 0) + 1

                # Chỉ thêm nếu chưa biết hoặc tìm được đường ngắn hơn
                if new_state not in g_score or new_g < g_score[new_state]:
                    g_score[new_state]  = new_g
                    parent[new_state]   = (current_state, action)

                    # GBFS: chỉ dùng h(n) để ưu tiên
                    h = self.heuristic(new_state, board)
                    tie_breaker += 1
                    heapq.heappush(pq, (h, tie_breaker, new_state))

            max_queue_size = max(max_queue_size, len(pq))

        return None, 0, expanded_nodes, max_queue_size
