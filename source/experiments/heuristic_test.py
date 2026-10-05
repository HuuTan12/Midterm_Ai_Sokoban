import sys
import os
from collections import deque

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from source.core.map_parser import MapParser
from source.core.rules import Rules
from source.search.astar import AStar

MAPS_DIR = os.path.join(os.path.dirname(__file__), '..', 'maps')

MAP_NAMES = ['Map1.txt', 'Map2.txt']
solver = AStar()

def compute_true_costs_along_path(start_state, board):
    print("  [INFO] Finding optimal solution path...")
    path, cost, _, _ = solver.search(start_state, board, timeout_seconds=60)
    
    if path is None:
        print(f"  [ERROR] Cannot find solution!")
        return {}, []

    print(f"  [INFO] Solution found! Evaluating admissibility and consistency along the optimal path (length {len(path)})...")
    
    costs = {}
    states_on_path = []
    
    cur_state = start_state
    for i in range(len(path)):
        costs[cur_state] = len(path) - i
        states_on_path.append(cur_state)
        
        action = path[i]
        for act, next_state in Rules.get_successors(cur_state, board):
            if act == action:
                cur_state = next_state
                break
                
    costs[cur_state] = 0
    states_on_path.append(cur_state)
    
    if not cur_state.is_goal(board):
        print(f"  [ERROR] The solver timed out and only found a partial path (not a goal).")
        return {}, []
    
    return costs, states_on_path

def run_test_for_map(map_name):
    map_path = os.path.join(MAPS_DIR, map_name)
    if not os.path.exists(map_path):
        return
        
    map_lines = MapParser.load_map(map_path)
    board, start_state = MapParser.parse_level(map_lines)
    
    print("=" * 60)
    print(f"  Heuristic Verification: {map_name}")
    print("=" * 60)

    true_costs, sampled_states = compute_true_costs_along_path(start_state, board)
    solvable = true_costs

    if not solvable:
        return

    admissible = True
    for state, h_star in solvable.items():
        if state.is_goal(board):
            continue
        h_cur = solver.heuristic(state, board)
        if h_cur > h_star:
            print(f"  [FAIL] Admissibility violated: h(n)={h_cur} > h*(n)={h_star}")
            print(f"         Agent: {state.agent}")
            print(f"         Boxes: {state.boxes}")
            print(f"         Goals: {board.goals}")
            misplaced = [b for b in state.boxes if not board.is_goal(b)]
            free_goals = list(board.goals - set(state.boxes))
            print(f"         Misplaced: {misplaced}")
            print(f"         Free Goals: {free_goals}")
            admissible = False
            break

    if admissible:
        print("  >>> RESULT: ADMISSIBLE [PASS]")
    else:
        print("  >>> RESULT: NOT ADMISSIBLE [FAIL]")

    consistent = True
    for state in sampled_states:
        h_cur = solver.heuristic(state, board)
        if h_cur == float('inf'):
            continue

        for _, next_state in Rules.get_successors(state, board):
            h_next = solver.heuristic(next_state, board)
            if h_cur > 1 + h_next:
                print(f"  [FAIL] Consistency violated: h(n)={h_cur} > 1 + h(n')={1 + h_next}")
                consistent = False
                break
        if not consistent:
            break

    if consistent:
        print("  >>> RESULT: CONSISTENT [PASS]")
    else:
        print("  >>> RESULT: NOT CONSISTENT [FAIL]")
    print()

def main():
    print("Starting Heuristic Verification on all Maps...\n")
    for map_name in MAP_NAMES:
        run_test_for_map(map_name)

if __name__ == "__main__":
    main()