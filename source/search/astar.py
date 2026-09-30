import heapq
from core.rules import Rules
from search.search_algorithm import SearchAlgorithm

def reconstruct_path(goal_state, parent):
    path = []
    current_state = goal_state

    while current_state in parent:
        previous_state, action = parent[current_state]
        path.append(action)
        current_state = previous_state

    path.reverse()
    return path

def chebyshev_distance(pos1, pos2):
    row1, col1 = pos1
    row2, col2 = pos2
    return max(abs(row1 - row2), abs(col1 - col2))

class AStar(SearchAlgorithm):
    def heuristic(self, state, board):
        misplaced_boxes = list(set(state.boxes) - board.goals)
        available_goals = list(board.goals - set(state.boxes))

        total = 0
        for box in misplaced_boxes:
            best_distance = float("inf")
            for goal in available_goals:
                distance = chebyshev_distance(box, goal)
                if distance < best_distance:
                    best_distance = distance
            total += best_distance
        return total

    def search(self, start_state, board):
        pq = []
        tie_breaker = 0

        g_score = {start_state: 0}
        h_score = self.heuristic(start_state, board)
        f_score = g_score[start_state] + h_score

        heapq.heappush(pq, (f_score, tie_breaker, start_state))

        visited = set()
        expanded_nodes = 0
        max_queue_size = 1
        parent = {}

        while pq:
            current_f, _, current_state = heapq.heappop(pq)

            if current_state.is_goal(board):
                path = reconstruct_path(current_state, parent)
                return path, g_score[current_state], expanded_nodes, max_queue_size

            if current_state in visited:
                continue

            visited.add(current_state)
            expanded_nodes += 1

            successors = Rules.get_successors(current_state, board)

            for action, new_state in successors:
                tentative_g = g_score[current_state] + 1

                if new_state not in visited and (new_state not in g_score or tentative_g < g_score[new_state]):
                    parent[new_state] = (current_state, action)
                    g_score[new_state] = tentative_g

                    h = self.heuristic(new_state, board)
                    f = tentative_g + h

                    tie_breaker += 1
                    heapq.heappush(pq, (f, tie_breaker, new_state))

                    max_queue_size = max(max_queue_size, len(pq))

        return None, 0, expanded_nodes, max_queue_size