class Board:
    def __init__(self, width, height, walls, goals):
        self.width = width
        self.height = height
        self.walls = frozenset(walls)
        self.goals = frozenset(goals)

    def is_wall(self, position):
        return position in self.walls

    def is_goal(self, position):
        return position in self.goals

    def is_within_bounds(self, position):
        row, col = position
        return 0 <= row < self.height and 0 <= col < self.width