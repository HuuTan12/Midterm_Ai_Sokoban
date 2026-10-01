from collections import deque
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

class BFS(SearchAlgorithm):
    def search(self, start_state, board, timeout_seconds=1.0):
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
            if time.time() - start_time > timeout_seconds:
                return None, 0, expanded_nodes, max_queue_size
                
            current_state = queue.popleft()
            
            if current_state.is_goal(board):
                path = reconstruct_path(current_state, parent)
                return path, len(path), expanded_nodes, max_queue_size
                
            expanded_nodes += 1
            successors = Rules.get_successors(current_state, board)

            for action, new_state in successors:
                if new_state not in visited:
                    visited.add(new_state)
                    parent[new_state] = (current_state, action)
                    queue.append(new_state)
                    
            max_queue_size = max(max_queue_size, len(queue))

        return None, 0, expanded_nodes, max_queue_size