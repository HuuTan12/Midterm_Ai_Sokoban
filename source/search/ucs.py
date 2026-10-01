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

class UCS(SearchAlgorithm):
    def search(self, start_state, board, timeout_seconds=1.0):
        import time
        start_time = time.time()
        priority_queue = []
        tie_breaker = 0
        expanded_nodes = 0
        max_queue_size = 1 

        heapq.heappush(priority_queue, (0, tie_breaker, start_state))

        visited = set()
        parent = {}
        cost_so_far = {start_state: 0}

        while priority_queue:
            if time.time() - start_time > timeout_seconds:
                return None, 0, expanded_nodes, max_queue_size

            current_fee, _, current_state = heapq.heappop(priority_queue)

            if current_state in visited:
                continue
            
            visited.add(current_state)
            expanded_nodes += 1

            if current_state.is_goal(board):
                path = reconstruct_path(current_state, parent)
                return path, current_fee, expanded_nodes, max_queue_size

            successors = Rules.get_successors(current_state, board)

            for action, new_state in successors:
                new_cost = current_fee + 1

                if new_state not in visited and (new_state not in cost_so_far or new_cost < cost_so_far[new_state]):
                    cost_so_far[new_state] = new_cost
                    parent[new_state] = (current_state, action)
                    
                    tie_breaker += 1
                    heapq.heappush(priority_queue, (new_cost, tie_breaker, new_state))
            
            max_queue_size = max(max_queue_size, len(priority_queue))
                    
        return None, 0, expanded_nodes, max_queue_size