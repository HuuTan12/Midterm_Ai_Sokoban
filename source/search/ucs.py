import heapq
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

class UCS(SearchAlgorithm):
    def search(self, start_state, board, timeout_seconds=30.0):
        import time
        start_time = time.time()
        pq = []
        tie = 0
        expanded = 0
        max_q = 1

        heapq.heappush(pq, (0, tie, start_state))
        visited = set()
        parent = {}
        cost = {start_state: 0}

        while pq:
            if time.time() - start_time > timeout_seconds:
                return None, 0, expanded, max_q

            g, _, state = heapq.heappop(pq)

            if state in visited:
                continue
            visited.add(state)
            expanded += 1

            if state.is_goal(board):
                path = reconstruct_path(state, parent)
                return path, g, expanded, max_q

            for action, next_state in Rules.get_successors(state, board):
                new_g = g + 1
                if next_state not in visited and (next_state not in cost or new_g < cost[next_state]):
                    cost[next_state] = new_g
                    parent[next_state] = (state, action)
                    tie += 1
                    heapq.heappush(pq, (new_g, tie, next_state))

            max_q = max(max_q, len(pq))

        return None, 0, expanded, max_q