class State:
    def __init__(self, agent_pos, boxes):
        self.agent_pos = agent_pos
        self.boxes = tuple(sorted(boxes))

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return self.agent_pos == other.agent_pos and self.boxes == other.boxes

    def __hash__(self):
        return hash((self.agent_pos, self.boxes))

    def is_goal(self, board):
        for box in self.boxes:
            if not board.is_goal(box):
                return False
        return True