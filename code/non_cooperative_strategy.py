import random
from environment import TerrainType, AntPerception
from ant import AntAction, AntStrategy

class NonCooperativeStrategy(AntStrategy):
    """
    Strategy where ants:
    1. Initialize memory with the colony position.
    2. Update memory with the closest food to the colony.
    3. Calculate the shortest path between food and the colony.
    """

    def __init__(self):
        self.memory = {}  # ant_id -> {"colony": tuple, "closest_food": tuple, "closest_distance": float}

    def decide_action(self, perception: AntPerception) -> AntAction:
        ant_id = perception.ant_id
        if ant_id not in self.memory:
            self.memory[ant_id] = {"colony": None, "closest_food": None, "closest_distance": float("inf")}

        mem = self.memory[ant_id]

        # Update memory with visible cells
        for rel_pos, terrain in perception.visible_cells.items():
            abs_pos = self._absolute_position(perception, rel_pos)
            if terrain == TerrainType.COLONY:
                mem["colony"] = abs_pos
            elif terrain == TerrainType.FOOD:
                self._update_closest_food(mem, abs_pos)

        # 1. If not carrying food, go to the closest known food
        if not perception.has_food:
            # If standing on food, pick it up
            if (0, 0) in perception.visible_cells and perception.visible_cells[(0, 0)] == TerrainType.FOOD:
                return AntAction.PICK_UP_FOOD
            # Otherwise, move towards the closest known food
            if mem["closest_food"]:
                return self._move_towards(perception, mem["closest_food"])
            # If no food is known, explore randomly
            return self._random_move()
        
        # 2. If carrying food, return to the colony
        else:
            # If standing on the colony, drop the food
            if (0, 0) in perception.visible_cells and perception.visible_cells[(0, 0)] == TerrainType.COLONY:
                return AntAction.DROP_FOOD
            # Otherwise, move towards the colony
            if mem["colony"]:
                return self._move_towards(perception, mem["colony"])
            # If the colony is not known, explore randomly
            return self._random_move()
        
    def _absolute_position(self, perception, rel_pos):
        """Calculate the absolute position based on the relative position."""
        return (rel_pos[0], rel_pos[1])

    def _update_closest_food(self, mem, food_pos):
        """Update the closest food to the colony in memory."""
        if mem["colony"]:
            distance = self._manhattan_distance(mem["colony"], food_pos)
            if distance < mem["closest_distance"]:
                mem["closest_food"] = food_pos
                mem["closest_distance"] = distance

    def _manhattan_distance(self, pos1, pos2):
        """Calculate the Manhattan distance between two positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def _move_towards(self, perception, target):
        """Move greedily towards the target."""
        dx = target[0]
        dy = target[1]

        if dy > 0:
            return AntAction.MOVE_FORWARD
        elif dx > 0:
            return AntAction.TURN_RIGHT
        elif dx < 0:
            return AntAction.TURN_LEFT
        else:
            return self._random_move()

    def _random_move(self):
        """Perform a random movement."""
        r = random.random()
        if r < 0.5:
            return AntAction.MOVE_FORWARD
        elif r < 0.75:
            return AntAction.TURN_LEFT
        else:
            return AntAction.TURN_RIGHT