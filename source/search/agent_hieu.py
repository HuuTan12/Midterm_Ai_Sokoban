import random
from collections import deque
from source.core.competitive_state import CompetitiveState
from source.core.board import Board


DIRECTIONS = ["North", "South", "East", "West"]
DELTA = {"North": (-1, 0), "South": (1, 0), "West": (0, -1), "East": (0, 1)}


def bfs_dist(start, goal, walls, width, height):
    if start == goal:
        return 0
    from collections import deque
    visited = {start}
    queue = deque([(start, 0)])
    while queue:
        pos, dist = queue.popleft()
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            npos = (pos[0] + dr, pos[1] + dc)
            if npos == goal:
                return dist + 1
            if (0 <= npos[0] < height and 0 <= npos[1] < width
                    and npos not in walls and npos not in visited):
                visited.add(npos)
                queue.append((npos, dist + 1))
    return float('inf')


def bfs_path(start, goal, walls, width, height):
    if start == goal:
        return []
    visited = {start}
    queue = deque([(start, [])])
    while queue:
        pos, path = queue.popleft()
        for d, (dr, dc) in DELTA.items():
            npos = (pos[0] + dr, pos[1] + dc)
            if npos == goal:
                return path + [d]
            if (0 <= npos[0] < height and 0 <= npos[1] < width
                    and npos not in walls and npos not in visited):
                visited.add(npos)
                queue.append((npos, path + [d]))
    return []


class AgentHieu:
    def __init__(self):
        self.name = "Agent Hieu (UCS)"
        self.path = []
        self.last_state_hash = None
        self.stuck_count = 0
        self.last_pos = None

    def _valid_moves(self, agent_pos, other_pos, board, all_boxes):
        moves = []
        for d, (dr, dc) in DELTA.items():
            np = (agent_pos[0] + dr, agent_pos[1] + dc)
            if not board.is_within_bounds(np) or board.is_wall(np):
                continue
            if np == other_pos:
                continue
            if np in all_boxes:
                nbp = (np[0] + dr, np[1] + dc)
                if not board.is_within_bounds(nbp) or board.is_wall(nbp) or nbp in all_boxes:
                    continue
            moves.append(d)
        return moves

    def _plan_push_box_to_goal(self, agent_pos, box_pos, goal_pos, board, all_boxes):
        if box_pos == goal_pos:
            return []

        h, w = board.height, board.width
        all_b = frozenset(all_boxes)

        start = (agent_pos, box_pos)
        visited = {start}
        queue = deque([(start, [])])

        while queue:
            (apos, bpos), actions = queue.popleft()
            if bpos == goal_pos:
                return actions

            if len(actions) > 60:
                continue

            for d, (dr, dc) in DELTA.items():
                n_apos = (apos[0] + dr, apos[1] + dc)
                if not (0 <= n_apos[0] < h and 0 <= n_apos[1] < w):
                    continue
                if board.is_wall(n_apos):
                    continue

                n_bpos = bpos
                if n_apos == bpos:
                    n_bpos = (bpos[0] + dr, bpos[1] + dc)
                    if not (0 <= n_bpos[0] < h and 0 <= n_bpos[1] < w):
                        continue
                    if board.is_wall(n_bpos):
                        continue
                    if n_bpos in all_b and n_bpos != bpos:
                        continue
                else:
                    if n_apos in all_b and n_apos != bpos:
                        continue

                state_key = (n_apos, n_bpos)
                if state_key not in visited:
                    visited.add(state_key)
                    queue.append((state_key, actions + [d]))

        return []

    def _plan_displace_box(self, agent_pos, box_pos, board, all_boxes):
        best_plan = []
        best_cost = float('inf')
        for d, (dr, dc) in DELTA.items():
            dest = (box_pos[0] + dr, box_pos[1] + dc)
            if not board.is_within_bounds(dest) or board.is_wall(dest):
                continue
            if dest in all_boxes:
                continue
            agent_need = (box_pos[0] - dr, box_pos[1] - dc)
            if not board.is_within_bounds(agent_need) or board.is_wall(agent_need):
                continue
            temp_walls = board.walls | (frozenset(all_boxes) - {box_pos})
            path = bfs_path(agent_pos, agent_need, temp_walls | {box_pos}, board.width, board.height)
            if path is None:
                path = []
            plan = path + [d]
            if len(plan) < best_cost:
                best_cost = len(plan)
                best_plan = plan
        return best_plan

    def _make_plan(self, state: CompetitiveState, board: Board):
        agent_pos = state.agent2_pos
        all_boxes = set(state.all_boxes)
        goals = board.goals

        neutral_on_goal  = [b for b in state.neutral_boxes if board.is_goal(b)]
        free_goals       = [g for g in goals if g not in all_boxes]
        my_unfinished    = [b for b in state.agent2_boxes if not board.is_goal(b)]
        enemy_on_goal    = [b for b in state.agent1_boxes if board.is_goal(b)]
        neutral_off_goal = [b for b in state.neutral_boxes if not board.is_goal(b)]

        if my_unfinished and free_goals:
            best_plan = []
            best_cost = float('inf')
            for box in my_unfinished:
                for goal in free_goals:
                    plan = self._plan_push_box_to_goal(agent_pos, box, goal, board, all_boxes)
                    if plan and len(plan) < best_cost:
                        best_cost = len(plan)
                        best_plan = plan
            if best_plan:
                return best_plan

        if neutral_off_goal and free_goals:
            best_plan = []
            best_cost = float('inf')
            for box in neutral_off_goal:
                for goal in free_goals:
                    plan = self._plan_push_box_to_goal(agent_pos, box, goal, board, all_boxes)
                    if plan and len(plan) < best_cost:
                        best_cost = len(plan)
                        best_plan = plan
            if best_plan:
                return best_plan

        if neutral_on_goal:
            target_c = min(neutral_on_goal, key=lambda b: bfs_dist(agent_pos, b, board.walls, board.width, board.height))
            plan = self._plan_displace_box(agent_pos, target_c, board, all_boxes)
            if plan:
                return plan

        if enemy_on_goal:
            target = min(enemy_on_goal, key=lambda b: bfs_dist(agent_pos, b, board.walls, board.width, board.height))
            plan = self._plan_displace_box(agent_pos, target, board, all_boxes)
            if plan:
                return plan

        return []

    def get_action(self, state: CompetitiveState, board: Board):
        agent_pos = state.agent2_pos
        if agent_pos is None:
            return None

        state_hash = hash(state)
        if state_hash != self.last_state_hash:
            self.path = []
            self.last_state_hash = state_hash

        if agent_pos == self.last_pos:
            self.stuck_count += 1
        else:
            self.stuck_count = 0
        self.last_pos = agent_pos

        if self.stuck_count >= 3:
            self.path = []
            self.stuck_count = 0
            all_boxes = set(state.all_boxes)
            valid = self._valid_moves(agent_pos, state.agent1_pos, board, all_boxes)
            return random.choice(valid) if valid else None

        if not self.path:
            self.path = self._make_plan(state, board)

        if len(self.path) == 0:
            return None


        if self.path:
            action = self.path.pop(0)
            if hasattr(action, 'value'):
                action = action.value
            return action

        all_boxes = set(state.all_boxes)
        valid = self._valid_moves(agent_pos, state.agent1_pos, board, all_boxes)
        return random.choice(valid) if valid else None