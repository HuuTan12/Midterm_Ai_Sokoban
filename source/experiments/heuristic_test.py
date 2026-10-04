import sys
import os
from collections import deque

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from source.core.map_parser import MapParser
from source.core.rules import Rules
from source.search.astar import AStar

MAP_PATH = os.path.join(os.path.dirname(__file__), '..', 'maps', 'Map1.txt')
map_lines = MapParser.load_map(MAP_PATH)
board, start_state = MapParser.parse_level(map_lines)
solver = AStar()

def get_all_reachable(start, board):
    visited = set()
    queue = deque([start])
    while queue:
        s = queue.popleft()
        if s in visited:
            continue
        visited.add(s)
        for _, ns in Rules.get_successors(s, board):
            if ns not in visited:
                queue.append(ns)
    return visited

def compute_true_costs(states, board):
    costs = {}
    for s in states:
        if s.is_goal(board):
            costs[s] = 0
            continue
        q = deque([(s, 0)])
        seen = set()
        found = False
        while q:
            cur, d = q.popleft()
            if cur in seen:
                continue
            seen.add(cur)
            if cur.is_goal(board):
                costs[s] = d
                found = True
                break
            for _, ns in Rules.get_successors(cur, board):
                if ns not in seen:
                    q.append((ns, d + 1))
        if not found:
            costs[s] = None
    return costs

print("=" * 60)
print("  REQUIREMENT 4 — Heuristic Verification")
print(f"  Map: {os.path.basename(MAP_PATH)}")
print("=" * 60)

all_states = get_all_reachable(start_state, board)
true_costs = compute_true_costs(all_states, board)
solvable = {s: c for s, c in true_costs.items() if c is not None}

admissible = True
for state, h_star in solvable.items():
    if state.is_goal(board):
        continue
    h = solver.heuristic(state, board)
    if h == float('inf'):
        continue
    if h > h_star:
        admissible = False
        break

if admissible:
    print("  >>> RESULT: ADMISSIBLE [PASS]")
else:
    print("  >>> RESULT: NOT ADMISSIBLE [FAIL]")

consistent = True
for state in all_states:
    h_cur = solver.heuristic(state, board)
    if h_cur == float('inf'):
        continue

    for action, next_state in Rules.get_successors(state, board):
        h_next = solver.heuristic(next_state, board)
        if h_next == float('inf'):
            continue
        
        cost = 1
        if h_cur > cost + h_next:
            consistent = False
            break

if consistent:
    print("  >>> RESULT: CONSISTENT [PASS]")
else:
    print("  >>> RESULT: NOT CONSISTENT [FAIL]")