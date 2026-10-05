import time
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from source.core.map_parser import MapParser
from source.search.ucs import UCS
from source.search.astar import AStar

MAPS_DIR   = os.path.join(os.path.dirname(__file__), '..', 'maps')
MAP_NAMES  = ['Map1.txt', 'Map2.txt', 'Map3.txt', 'Map4.txt']
TIMEOUT    = 10
N_RUNS     = 1

def run_one(solver_cls, board, start_state):
    t0 = time.perf_counter()
    path, cost, expanded, max_q = solver_cls().search(
        start_state, board, timeout_seconds=TIMEOUT
    )
    elapsed = time.perf_counter() - t0
    return elapsed, path, cost, expanded, max_q

def benchmark_map(map_path):
    map_name = os.path.basename(map_path)
    map_lines = MapParser.load_map(map_path)
    board, start_state = MapParser.parse_level(map_lines)
    
    print(f"\nBenchmarking: {map_name}")
    print("-" * 72)
    print(f"{'Algorithm':<22} | {'Avg Time (s)':<14} | {'Expanded Nodes':<16} | {'Max Queue':<12} | {'Cost'}")
    print("-" * 72)

    for label, solver_cls in [("UCS", UCS), ("A*", AStar)]:
        elapsed0, path0, cost0, expanded0, max_q0 = run_one(solver_cls, board, start_state)

        if path0 is None:
            print(f"  {label:<20} | {'TIMEOUT':<14} | {expanded0:>16,} | {max_q0:>12,} | -")
            continue

        total_time = elapsed0
        for _ in range(N_RUNS - 1):
            t, _, _, _, _ = run_one(solver_cls, board, start_state)
            total_time += t
        avg_time = total_time / N_RUNS

        print(f"  {label:<20} | {avg_time:<14.6f} | {expanded0:>16,} | {max_q0:>12,} | {cost0}")

    print("-" * 72)

def main():
    for map_name in MAP_NAMES:
        map_path = os.path.join(MAPS_DIR, map_name)
        if os.path.exists(map_path):
            benchmark_map(map_path)

if __name__ == "__main__":
    main()