import os
from core.map_parser import MapParser
from search.bfs import bfs


# Đọc map
base_dir = os.path.dirname(os.path.abspath(__file__))
map_path = os.path.join(base_dir, "maps", "example_map.txt")
lines = MapParser.load_map(map_path)

# Parse thành Board và State
board, state = MapParser.parse_level(lines)

# Chạy BFS
solution = bfs(state, board)

# In kết quả
print("=== BFS RESULT ===")

if solution is None:
    print("Không tìm thấy lời giải.")
else:
    print("Solution:", solution)
    print("Number of steps:", len(solution))