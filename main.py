import sys
import os

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
SRC_DIR  = os.path.join(ROOT_DIR, 'source')
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, SRC_DIR)


def print_usage():
    print("=" * 45)
    print("   SOKOBAN AI - Nhom Hieu")
    print("=" * 45)
    print("Chon che do chay:")
    print("  1. Sokoban 1 Agent (Requirement 5) - UCS / A*")
    print("  2. Sokoban Competitive 2 Agents (Requirement 8)")
    print("=" * 45)


if __name__ == "__main__":
    print_usage()
    try:
        choice = input("Nhap so (1 hoac 2): ").strip()
        if choice == '1':
            from source.gui.game import Game
            from source.gui.main import main
            main()

        elif choice == '2':
            try:
                n_steps = int(input("Nhap so buoc toi da (n) [mac dinh 50]: ").strip() or "50")
            except ValueError:
                n_steps = 50
                print("Khong hop le, mac dinh n = 50.")
            from source.competitive_gui.main import main as comp_main
            comp_main(n_steps)

        else:
            print("Lua chon khong hop le. Thoat.")
    except KeyboardInterrupt:
        print("\nDa thoat.")