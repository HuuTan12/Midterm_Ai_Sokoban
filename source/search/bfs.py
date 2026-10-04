from collections import deque
from core.rules import Rules
from search.search_algorithm import SearchAlgorithm

def reconstruct_path(goal_state, parent):
    path = []
    current = goal_state
    while current in parent:
        prev, action = parent[current]
        path.append(action)
        current = prev
    path.reverse()
    return path

class BFS(SearchAlgorithm):
    def search(self, start_state, board, timeout_seconds=30.0):
        import time
        start_time = time.time()
        queue = deque()
        visited = set()
        parent = {}
        expanded = 0
        max_q = 1

        queue.append(start_state)
        visited.add(start_state)

        while queue:
            if time.time() - start_time > timeout_seconds:
                return None, 0, expanded, max_q

            state = queue.popleft()
            expanded += 1

            if state.is_goal(board):
                path = reconstruct_path(state, parent)
                return path, len(path), expanded, max_q

            for action, next_state in Rules.get_successors(state, board):
                if next_state not in visited:
                    visited.add(next_state)
                    parent[next_state] = (state, action)
                    queue.append(next_state)

            max_q = max(max_q, len(queue))

        return None, 0, expanded, max_q