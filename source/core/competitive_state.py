class CompetitiveState:
    def __init__(self, agent1_pos, agent2_pos, neutral_boxes, agent1_boxes, agent2_boxes):
        self.agent1_pos    = agent1_pos
        self.agent2_pos    = agent2_pos
        self.neutral_boxes = tuple(sorted(neutral_boxes))
        self.agent1_boxes  = tuple(sorted(agent1_boxes))
        self.agent2_boxes  = tuple(sorted(agent2_boxes))

    @property
    def all_boxes(self):
        return self.neutral_boxes + self.agent1_boxes + self.agent2_boxes

    def get_score(self, board):
        score1 = sum(1 for box in self.agent1_boxes if board.is_goal(box))
        score2 = sum(1 for box in self.agent2_boxes if board.is_goal(box))
        return score1, score2

    def get_goals_with_neutral(self, board):
        return frozenset(b for b in self.neutral_boxes if board.is_goal(b))

    def get_free_goals(self, board):
        occupied = set(self.all_boxes)
        return frozenset(g for g in board.goals if g not in occupied)

    def __eq__(self, other):
        if not isinstance(other, CompetitiveState):
            return False
        return (self.agent1_pos == other.agent1_pos and
                self.agent2_pos == other.agent2_pos and
                self.neutral_boxes == other.neutral_boxes and
                self.agent1_boxes == other.agent1_boxes and
                self.agent2_boxes == other.agent2_boxes)

    def __hash__(self):
        return hash((self.agent1_pos, self.agent2_pos,
                     self.neutral_boxes, self.agent1_boxes, self.agent2_boxes))
