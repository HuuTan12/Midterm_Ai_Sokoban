from core.map_parser import MapParser
from search.ucs import UCS

def test_ucs_algorithm():
    # 1. Load bản đồ
    map_path = "maps/example_map.txt"
    print(f"Đang nạp bản đồ từ: {map_path}...")
    
    lines = MapParser.load_map(map_path)
    board, init_state = MapParser.parse_level(lines)

    # 2. Khởi chạy UCS
    print("AI đang tính toán đường đi bằng UCS...")
    path, cost, expanded, max_q = UCS().search(init_state, board)

    # 3. Chốt kết quả
    if path:
        print("\n✅ TÌM THẤY GIẢI PHÁP!")
        print(f"Tổng chi phí (Cost): {cost}")
        print(f"Số bước đi: {len(path)}")
        print(f"Chi tiết hành động:\n{path}")
    else:
        print("\n❌ TRẠNG THÁI BẾ TẮC: Không tìm thấy đường đi!")

if __name__ == "__main__":
    test_ucs_algorithm()