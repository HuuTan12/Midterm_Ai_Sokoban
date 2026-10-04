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

class AStar(SearchAlgorithm):
    def heuristic(self, state, board):
        misplaced = list(set(state.boxes) - board.goals)
        free_goals = list(board.goals - set(state.boxes))
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

        g = {start_state: 0}
        h = self.heuristic(start_state, board)
        heapq.heappush(pq, (g[start_state] + h, tie, start_state))
        visited = set()
        parent = {}

        best_state = start_state
        best_h = h

        while pq:
            if time.time() - start_time > timeout_seconds:
                if best_state != start_state:
                    return reconstruct_path(best_state, parent), g.get(best_state, 0), expanded, max_q
                return None, 0, expanded, max_q

            f, _, state = heapq.heappop(pq)

            if state.is_goal(board):
                path = reconstruct_path(state, parent)
                return path, g[state], expanded, max_q

            if state in visited:
                continue
            visited.add(state)
            expanded += 1

            for action, next_state in Rules.get_successors(state, board):
                new_g = g[state] + 1
                if next_state not in visited and (next_state not in g or new_g < g[next_state]):
                    parent[next_state] = (state, action)
                    g[next_state] = new_g
                    new_h = self.heuristic(next_state, board)
                    
                    if new_h < best_h:
                        best_h = new_h
                        best_state = next_state
                        
                    tie += 1
                    heapq.heappush(pq, (new_g + new_h, tie, next_state))
                    max_q = max(max_q, len(pq))

        return None, 0, expanded, max_q