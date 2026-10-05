# Presentation Slide Outline (Sokoban AI Project)

> **Formatting Notes (Mandatory):**
> - Aspect Ratio: **4:3**
> - Background: **White or light-colored** (Strictly avoid dark backgrounds or overly colorful shapes to ensure grayscale printing compatibility).
> - Presentation duration: **Max 5 minutes** (Aim for 7-8 slides).
> - **DO NOT embed raw source code in the slides.**

---

## Slide 1: Title Slide
- **Project Title:** Midterm Project - Sokoban AI & Competitive Multi-Agent
- **Course:** Artificial Intelligence
- **Group Name:** [Your Group Name]
- **Team Members:** 
  - [Student 1 Name] - [Student 1 ID]
  - [Student 2 Name] - [Student 2 ID]

---

## Slide 2: Student List & Roles
*(Format as a Table)*

| Student ID | Full Name | Email Address | Assigned Tasks | % Completion |
| :--- | :--- | :--- | :--- | :--- |
| 12345678 | Nguyen Huu Tan | tan@email.com | Design A* Heuristic, Implement Competitive Rules | 100% |
| 87654321 | [Hieu's Name] | hieu@email.com | Implement UCS, Build AgentTan & AgentHieu Logic | 100% |
*(Remember to replace with real information)*

---

## Slide 3: Task Completion Summary
*(Format as a Table)*

| Task | Description | Status | % Completion |
| :--- | :--- | :--- | :--- |
| **Task 1** | Implement UCS & A* for standard Sokoban | Done | 100% |
| **Task 1.1** | Propose custom Heuristic (No Manhattan/Euclidean) | Done | 100% |
| **Task 2** | Implement Competitive Agents (Agent vs Agent) | Done | 100% |
| **Task 2.1** | Handle "C" Box (Neutral on goal) mechanics | Done | 100% |
| **Task 3** | Presentation & Report | Done | 100% |

---

## Slide 4: Single Player Approach (A* & UCS)
**1. Uniform Cost Search (UCS):**
- Explores the state space with a uniform path cost.
- Guarantees the optimal (shortest) path but expands a massive number of nodes.

**2. A* Search with Custom Heuristic:**
- Constraint: **Manhattan and Euclidean distances are NOT allowed.**
- **Proposed Heuristic:** Bipartite Matching (Hungarian Algorithm) combined with True BFS Distance and Deadlock Detection.
  
**Heuristic Pseudocode:**
```text
Function Heuristic(state):
    If state contains Corner_Deadlock:
        Return INFINITY
        
    Misplaced_Boxes = get_boxes_not_on_goal(state)
    Free_Goals = get_empty_goals(state)
    
    // Use True BFS Distance (grid pathfinding) instead of Manhattan
    Cost_Matrix = Calculate_BFS_Distance_Matrix(Misplaced_Boxes, Free_Goals)
    
    Return Hungarian_Minimum_Cost(Cost_Matrix)
```

---

## Slide 5: Competitive Mode Approach (Multi-Agent)
- Two agents compete simultaneously on the same map. Both must make decisions under a strict time limit (< 1000ms).
- **Decision-Making Logic:** Utilizes a Depth-Limited Breadth-First Search (BFS) combined with a Priority System for real-time reactions.

**Agent Decision Pseudocode:**
```text
Function Get_Action(Current_State):
    If Agent is Stuck (position unchanged for 3 turns):
        Return Random_Valid_Move()
        
    // Priority System
    If (Has path to push OWN BOX to FREE GOAL):
        Return Next_Step(Path)
        
    If (Has path to push NEUTRAL BOX to FREE GOAL):
        Return Next_Step(Path)
        
    If (Has path to displace "C" BOX (Neutral on Goal)):
        Return Next_Step(Path)
        
    If (Has path to displace ENEMY BOX from Goal):
        Return Next_Step(Path)
        
    Return Random_Valid_Move()
```

---

## Slide 6: Advantages of Proposed Approaches
- **Strict Rule Compliance:** The A* custom heuristic strictly adheres to the "No Euclidean/Manhattan" rule by computing true BFS grid distances.
- **High Performance (< 1000ms):** In Competitive Mode, agents use depth-limited local BFS instead of a global A* search. Responses take only a few milliseconds, easily beating the 1000ms limit.
- **Robust Collision Handling:** The custom Competitive Rules engine smoothly resolves 5 different collision edge cases (e.g., head-to-head pushes, simultaneous box pushing).
- **Smart "C" Box Strategy:** Agents correctly recognize the neutral "C" box on a goal, intentionally pushing it off to claim ownership, then pushing it back in to score a point.

---

## Slide 7: Disadvantages of Proposed Approaches
- **Myopic Behavior in Competitive Mode:** The depth-limited BFS (capped at 50-60 steps) ensures speed but can cause agents to lose sight of boxes that are extremely far away on giant maps.
- **A* Heuristic Computation Overhead:** While highly accurate, combining the Hungarian matching algorithm with multiple BFS distance calculations consumes more CPU cycles per node compared to a simple Manhattan distance. This slightly slows down the node expansion rate on very complex maps.

---

## Slide 8: Q&A
- **Q&A / Live Demo**
- Thank you for your time and attention!
