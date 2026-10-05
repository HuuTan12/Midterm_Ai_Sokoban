# Sokoban AI & Competitive Multi-Agent Project

## 1. Introduction
This project is a Midterm Assignment for the Artificial Intelligence course. It involves developing search algorithms to solve the classic Sokoban puzzle game, as well as designing an AI system for a Competitive Mode where two AI Agents compete against each other in real-time on the same map.

The project features two main modes:
1. **Single-Player Mode:** Utilizes Uniform Cost Search (UCS) and A* Search algorithms to find the optimal path to solve standard Sokoban levels.
2. **Competitive Mode:** Two AI Agents (Agent_Tan and Agent_Hieu) compete to push boxes and score points in real-time with strict constraints (decision time < 1000ms per step).

---

## 2. System Requirements
- Python 3.8+
- `pygame` library (Used for GUI rendering)

**Installation:**
```bash
pip install pygame
```

---

## 3. Project Structure
The project is organized following an MVC-like architecture:
- `source/core/`: Contains core game logic (Map Parser, Board, Rules, Competitive State, Competitive Rules).
- `source/search/`: Contains the AI algorithms.
  - `ucs.py`: Uniform Cost Search algorithm (no heuristic).
  - `astar.py`: A* Search algorithm with a Custom Heuristic (Hungarian + BFS Distance).
  - `agent_tan.py` & `agent_hieu.py`: The decision-making logic for the two competitive bots.
- `source/gui/`: Contains the Main Menu UI.
- `source/competitive/`: Logic and rendering for the Competitive Multi-Agent mode.
- `source/maps/`: Text files (`.txt`) representing the map layouts (Map1 -> Map4).
- `main.py`: The entry point to run the application.

---

## 4. Technical Highlights

### A. Custom A* Heuristic (Strictly adhering to requirements)
The assignment strictly prohibits the use of **Manhattan or Euclidean distances**. Therefore, the A* heuristic is designed as follows:
1. **BFS Distance Metric:** Instead of geometric distances, the system calculates the actual number of steps on the grid, pathfinding around walls using Breadth-First Search (BFS).
2. **Hungarian Algorithm (Minimum Bipartite Matching):** Calculates the optimal minimum cost to pair $N$ misplaced boxes with $M$ empty goals.
3. **Corner Deadlock Detection:** Identifies boxes stuck in corners. If a deadlock is detected, the Heuristic returns `INFINITY`, allowing A* to immediately prune useless branches.

### B. Competitive Logic (Multi-Agent)
- **Ownership Mechanics:** Whoever pushes a box last gains ownership of it. Scoring only occurs when an agent pushes their owned box onto a goal.
- **The "C" Box (Neutral on Goal):** The map contains a neutral box "C" already placed on a goal. It grants 0 points initially. Agents must push it off the goal (claiming ownership), then push it back onto a goal to score a point.
- **Decision-Making < 1000ms:** Instead of running a heavy global A* search, the agents use a **Depth-Limited BFS** with a priority system to ensure decisions are made in milliseconds.
  **Priority Queue:**
  1. Push OWN box to an empty goal.
  2. Push NEUTRAL box to an empty goal.
  3. Displace the "C" box (neutral on goal) to claim the spot.
  4. Displace an ENEMY box from a goal to sabotage their score.
  5. Anti-stuck: If stuck (position unchanged for 3 turns) -> Make a random valid move to reset the state.

---

## 5. How to Run

1. Open a terminal in the root directory of the project.
2. Execute the following command:
   ```bash
   python main.py
   ```
3. The Game Menu will appear. Use the **Arrow Keys** to navigate:
   - **Single Player Mode:** Select an algorithm (e.g., A* or UCS), then select a Map.
   - **Competitive Mode:** Press the `C` key at the Main Menu to enter the 2-Agent competitive mode.
4. **Competitive Mode Controls:**
   - `<Space>`: Play / Pause simulation.
   - `Left / Right Arrows`: Step-by-step playback.
   - `ESC`: Return to the Main Menu.