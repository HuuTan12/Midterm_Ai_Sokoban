import heapq
from itertools import permutations
from source.core.rules import Rules
from source.search.search_algorithm import SearchAlgorithm

def reconstruct_path(goal_state, parent):
    path = []
    current = goal_state
    while current in parent:
        prev, action = parent[current]
        path.append(action)
        current = prev
    path.reverse()
    return path

def chebyshev(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

def is_corner_deadlock(box, board):
    if board.is_goal(box):
        return False
    r, c = box
    top = board.is_wall((r - 1, c))
    bottom = board.is_wall((r + 1, c))
    left = board.is_wall((r, c - 1))
    right = board.is_wall((r, c + 1))
    return (top or bottom) and (left or right)

def hungarian_min_cost(boxes, goals):
    if not boxes or not goals:
        return 0
    n = len(boxes)
    m = len(goals)
    best = float('inf')
    
    if n <= m:
        for perm in permutations(goals, n):
            cost = sum(chebyshev(b, g) for b, g in zip(boxes, perm))
            if cost < best:
                best = cost
    else:
        for perm in permutations(boxes, m):
            cost = sum(chebyshev(b, g) for b, g in zip(perm, goals))
            if cost < best:
                best = cost
    return best

class AStar(SearchAlgorithm):
    def heuristic(self, state, board):
        misplaced = [b for b in state.boxes if not board.is_goal(b)]
        if not misplaced:
            return 0
            
        for box in misplaced:
            if is_corner_deadlock(box, board):
                return float('inf')
                
        free_goals = list(board.goals - set(state.boxes))
        return hungarian_min_cost(misplaced, free_goals)

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
        best_h = h if h != float('inf') else 0

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

                    if new_h != float('inf'):
                        if new_h < best_h:
                            best_h = new_h
                            best_state = next_state

                        tie += 1
                        heapq.heappush(pq, (new_g + new_h, tie, next_state))
                        max_q = max(max_q, len(pq))

        return None, 0, expanded, max_q