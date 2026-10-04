import heapq
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

        best_state = start_state
        
        def simple_h(st):
            misplaced = list(set(st.boxes) - board.goals)
            free_goals = list(board.goals - set(st.boxes))
            t = 0
            for box in misplaced:
                best = min((max(abs(box[0] - g[0]), abs(box[1] - g[1])) for g in free_goals), default=0)
                t += best
            if misplaced:
                agent_to_box = min(max(abs(st.agent_pos[0] - b[0]), abs(st.agent_pos[1] - b[1])) for b in misplaced)
                t += agent_to_box
            return t
            
        best_h = simple_h(start_state)

        while pq:
            if time.time() - start_time > timeout_seconds:
                if best_state != start_state:
                    return reconstruct_path(best_state, parent), cost.get(best_state, 0), expanded, max_q
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
                    
                    nh = simple_h(next_state)
                    if nh < best_h:
                        best_h = nh
                        best_state = next_state
                        
                    tie += 1
                    heapq.heappush(pq, (new_g, tie, next_state))

            max_q = max(max_q, len(pq))

        return None, 0, expanded, max_q