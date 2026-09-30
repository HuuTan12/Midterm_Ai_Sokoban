import sys
import os

# Thêm đường dẫn để nhận diện module source
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def print_usage():
    print("Chọn chế độ chạy:")
    print("1. Chạy Sokoban 1 Agent (Requirement 5)")
    print("2. Chạy Sokoban Competitive 2 Agents (Requirement 8)")
    
if __name__ == "__main__":
    print_usage()
    try:
        choice = input("Nhập số (1 hoặc 2): ")
        if choice == '1':
            from source.gui import main as gui_main
            gui_main.main()
        elif choice == '2':
            try:
                n_steps = int(input("Nhập số bước tối đa (n) cho trận đấu: "))
            except ValueError:
                n_steps = 50
                print("Không hợp lệ, mặc định n = 50.")
            from source.competitive_gui import main as comp_main
            comp_main.main(n_steps)
        else:
            print("Lựa chọn không hợp lệ.")
    except KeyboardInterrupt:
        print("\nĐã thoát.")
