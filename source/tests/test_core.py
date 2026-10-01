import os
from core.map_parser import MapParser
from core.rules import Rules


# 1. Đọc file map
base_dir = os.path.dirname(os.path.abspath(__file__))
map_path = os.path.join(base_dir, "maps", "example_map.txt")
lines = MapParser.load_map(map_path)

# 2. Parse map thành Board và State
board, state = MapParser.parse_level(lines)

# 3. In thông tin để kiểm tra
print("=== BOARD ===")
print("Width:", board.width)
print("Height:", board.height)
print("Walls:", board.walls)
print("Goals:", board.goals)

print("\n=== STATE ===")
print("Agent:", state.agent_pos)
print("Boxes:", state.boxes)

# 4. Sinh các trạng thái kế tiếp
successors = Rules.get_successors(state, board)

print("\n=== SUCCESSORS ===")

for action, new_state in successors:
    print("Action:", action)
    print("Agent:", new_state.agent_pos)
    print("Boxes:", new_state.boxes)
    print("---")