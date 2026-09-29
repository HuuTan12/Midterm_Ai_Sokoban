from collections import deque

from core.map_parser import MapParser
from core.rules import Rules
from search.astar import heuristic


map_lines = MapParser.load_map("maps/example_map.txt")
board, start_state = MapParser.parse_level(map_lines)


def get_all_states(start_state, board):
    visited = set()
    queue = deque([start_state])

    while queue:
        current_state = queue.popleft()

        if current_state in visited:
            continue

        visited.add(current_state)

        for _, new_state in Rules.get_successors(current_state, board):
            if new_state not in visited:
                queue.append(new_state)

    return visited


def calculate_cost_to_goal(states, board):
    costs = {}

    for start_state in states:
        queue = deque([(start_state, 0)])
        visited = set()

        while queue:
            current_state, cost = queue.popleft()

            if current_state in visited:
                continue

            visited.add(current_state)

            if current_state.is_goal(board):
                costs[start_state] = cost
                break

            for _, new_state in Rules.get_successors(current_state, board):
                if new_state not in visited:
                    queue.append((new_state, cost + 1))

    return costs


states = get_all_states(start_state, board)
real_costs = calculate_cost_to_goal(states, board)

print("Total states:", len(states))

print("\n========== ADMISSIBILITY ==========")

admissible = True

for state in states:
    if state.is_goal(board):
        continue

    if state not in real_costs:
        continue

    h = heuristic(state, board)
    real_cost = real_costs[state]

    if h > real_cost:
        print("Vi phạm tại state:", state.agent_pos, state.boxes)
        print("h(n):", h)
        print("cost to goal:", real_cost)

        admissible = False
        break

if admissible:
    print("Heuristic is admissible.")
else:
    print("Heuristic is NOT admissible.")


print("\n========== CONSISTENCY ==========")

consistent = True

for state in states:
    h_current = heuristic(state, board)

    for action, new_state in Rules.get_successors(state, board):
        h_next = heuristic(new_state, board)

        cost = 1

        if h_current > cost + h_next:
            print("Vi phạm tại:")
            print("State:", state.agent_pos, state.boxes)
            print("Action:", action)
            print("Next state:", new_state.agent_pos, new_state.boxes)
            print("h(n):", h_current)
            print("cost:", cost)
            print("h(n'):", h_next)

            consistent = False
            break

    if not consistent:
        break

if consistent:
    print("Heuristic is consistent.")
else:
    print("Heuristic is NOT consistent.")