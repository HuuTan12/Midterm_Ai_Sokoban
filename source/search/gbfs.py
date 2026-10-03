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

def chebyshev(pos1, pos2):
    return max(abs(pos1[0] - pos2[0]), abs(pos1[1] - pos2[1]))

class GBFS(SearchAlgorithm):
    def heuristic(self, state, board):
        misplaced = list(set(state.boxes) - board.goals)
        free_goals = list(board.goals - set(state.boxes))
        if not misplaced:
            return 0
        total = 0
        for box in misplaced:
            best = min((chebyshev(box, g) for g in free_goals), default=0)
            total += best
        return total

    def search(self, start_state, board, timeout_seconds=30.0):
        import time
        start_time = time.time()
        pq = []
        tie = 0
        expanded = 0
        max_q = 1

        h0 = self.heuristic(start_state, board)
        heapq.heappush(pq, (h0, tie, start_state))
        visited = set()
        parent = {}
        g_score = {start_state: 0}

        while pq:
            if time.time() - start_time > timeout_seconds:
                return None, 0, expanded, max_q

            _, _, state = heapq.heappop(pq)

            if state in visited:
                continue
            visited.add(state)
            expanded += 1

            if state.is_goal(board):
                path = reconstruct_path(state, parent)
                return path, g_score.get(state, len(path)), expanded, max_q

            for action, next_state in Rules.get_successors(state, board):
                if next_state in visited:
                    continue
                new_g = g_score.get(state, 0) + 1
                if next_state not in g_score or new_g < g_score[next_state]:
                    g_score[next_state] = new_g
                    parent[next_state] = (state, action)
                    h = self.heuristic(next_state, board)
                    tie += 1
                    heapq.heappush(pq, (h, tie, next_state))

            max_q = max(max_q, len(pq))

        return None, 0, expanded, max_q
