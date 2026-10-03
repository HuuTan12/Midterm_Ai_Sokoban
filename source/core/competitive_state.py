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
