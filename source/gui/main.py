import pygame
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC_DIR  = os.path.join(ROOT_DIR, 'source')
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, SRC_DIR)

from source.gui.game import Game


def main():
    """Entry point cho chế độ 1 Agent (Requirement 5)."""
    maps_dir = os.path.join(ROOT_DIR, "source", "maps")
    map_paths = []
    if os.path.exists(maps_dir):
        for fname in sorted(os.listdir(maps_dir)):
            if fname.endswith(".txt"):
                map_paths.append(os.path.join(maps_dir, fname))

    if not map_paths:
        print("[CANH BAO] Khong tim thay map nao trong source/maps/")
        return

    Game(map_paths).run()


if __name__ == "__main__":
    main()
