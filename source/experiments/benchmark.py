import time
import os

from core.map_parser import MapParser
from search.ucs import ucs
from search.astar import astar


def run_benchmark(map_path):
    print(f"Benchmarking on: {os.path.basename(map_path)}")

    map_lines = MapParser.load_map(map_path)
    board, start_state = MapParser.parse_level(map_lines)

    number_of_runs = 100

    ucs_total_time = 0
    astar_total_time = 0

    ucs_result = None
    astar_result = None

    for _ in range(number_of_runs):
        start_time = time.perf_counter()
        ucs_result = ucs(start_state, board)
        ucs_total_time += time.perf_counter() - start_time

    for _ in range(number_of_runs):
        start_time = time.perf_counter()
        astar_result = astar(start_state, board)
        astar_total_time += time.perf_counter() - start_time

    ucs_time = ucs_total_time / number_of_runs
    astar_time = astar_total_time / number_of_runs

    print("-" * 70)
    print(
        f"{'Algorithm':<20} | "
        f"{'Time (s)':<15} | "
        f"{'Expanded Nodes':<15} | "
        f"{'Max Queue'}"
    )
    print("-" * 70)

    print(
        f"{'UCS':<20} | "
        f"{ucs_time:<15.6f} | "
        f"{ucs_result[2]:<15} | "
        f"{ucs_result[3]}"
    )

    print(
        f"{'A* (Chebyshev)':<20} | "
        f"{astar_time:<15.6f} | "
        f"{astar_result[2]:<15} | "
        f"{astar_result[3]}"
    )

    print("-" * 70)
    print(f"Number of runs: {number_of_runs}")

    print("\n========== RESULT ==========")
    print("UCS Cost:", ucs_result[1])
    print("A* Cost:", astar_result[1])

    print("UCS Path:", ucs_result[0])
    print("A* Path:", astar_result[0])


if __name__ == "__main__":
    map_file = "maps/example_map.txt"

    if os.path.exists(map_file):
        run_benchmark(map_file)
    else:
        print(
            f"Lỗi: Không tìm thấy file {map_file}. "
            f"Hãy chắc chắn bạn đang chạy từ thư mục 'source'."
        )
