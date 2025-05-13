import random
from ant import AntAction, AntStrategy
from common import TerrainType, AntPerception

class NonCooperativeStrategy(AntStrategy):
    """
    Stratégie non coopérative : chaque fourmi agit pour maximiser sa propre collecte de nourriture,
    sans coordination avec les autres. Elle ne tient pas compte des phéromones déposées par d'autres.
    """

    def __init__(self):
        self.memory = {}

    def sees_colony(self, perception):
        return TerrainType.COLONY in [cell for cell in perception.visible_cells.values()]
    
    def sees_food(self, perception):
        return TerrainType.FOOD in [cell for cell in perception.visible_cells.values()]
    
    def is_standing_on_colony(self, perception):
        return perception.visible_cells[(0, 0)] == TerrainType.COLONY
    
    def is_standing_on_food(self, perception):
        return perception.visible_cells[(0, 0)] == TerrainType.FOOD
    
    def has_food(self, perception):
        return perception.has_food
    
    def drop_food(self):
        return AntAction.DROP_FOOD
    
    def pickup_food(self):
        return AntAction.PICK_UP_FOOD
    
    def turn_left(self):
        return AntAction.TURN_LEFT
    
    def turn_right(self):
        return AntAction.TURN_RIGHT

    def move_forward(self):
        return AntAction.MOVE_FORWARD
    
    def is_in_the_opposite_direction(self, perception, direction):
        return perception.direction.value == (direction + 4) % 8
    
    def is_in_the_same_direction(self, perception, direction):
        return perception.direction.value == direction
    
    def get_direction_to_origin(self, fr):
        x, y = fr[0], fr[1]
        if x > 0:
            dx = 1
        elif x < 0:
            dx = -1
        else:
            dx = 0
        if y > 0:
            dy = 1
        elif y < 0:
            dy = -1
        else:
            dy = 0
        directions = {
            (0, -1): 2,   # NORTH
            (1, -1): 1,   # NORTHEAST
            (1, 0): 0,    # EAST
            (1, 1): 7,    # SOUTHEAST
            (0, 1): 6,    # SOUTH
            (-1, 1): 5,   # SOUTHWEST
            (-1, 0): 4,   # WEST
            (-1, -1): 3   # NORTHWEST
        }
        if (dx, dy) == (0, 0):
            return None
        else:
            return directions[(dx, dy)]
        
    def get_direction_to_food(self, pos):
        x, y = pos[0], pos[1]
        if x > 0:
            dx = 1
        elif x < 0:
            dx = -1
        else:
            dx = 0
        if y > 0:
            dy = 1
        elif y < 0:
            dy = -1
        else:
            dy = 0
        directions = {
            (0, -1): 6,   # NORTH
            (1, -1): 5,   # NORTHEAST
            (1, 0): 4,    # EAST
            (1, 1): 3,    # SOUTHEAST
            (0, 1): 2,    # SOUTH
            (-1, 1): 1,   # SOUTHWEST
            (-1, 0): 0,   # WEST
            (-1, -1): 7   # NORTHWEST
        }
        if (dx, dy) == (0, 0):
            return None
        else:
            return directions[(dx, dy)]

    def decide_action(self, perception: AntPerception) -> AntAction:
        ant_id = perception.ant_id
        if ant_id not in self.memory:
            self.memory[ant_id] = {
                "food_pos": [0, 0],
                "colony_pos": [0,0],
                "relative_pos": [0,0],
                "knows_path" : False
            }

        mem = self.memory[ant_id]

        

        if self.has_food(perception):
            if self.sees_colony(perception):
                if self.is_standing_on_colony(perception):
                    mem["relative_pos"] = [0,0]
                    return self.drop_food()
                else:
                    action = self._move_towards_direction(perception.direction, perception.get_colony_direction())
                    if action == AntAction.MOVE_FORWARD:
                        mem["relative_pos"][0] += self.updateRelativePos(perception)[0]
                        mem["relative_pos"][1] += self.updateRelativePos(perception)[1]
                    return action
            else:
                # Aller vers (0,0)
                direction = self.get_direction_to_origin(mem["relative_pos"])
                if direction is not None:
                    action = self._move_towards_direction(perception.direction, direction)
                    if action == AntAction.MOVE_FORWARD:
                        mem["relative_pos"][0] += self.updateRelativePos(perception)[0]
                        mem["relative_pos"][1] += self.updateRelativePos(perception)[1]
                    return action
                else:
                    return self._random_move()
        else :
            if mem["knows_path"]:
                if self.sees_food(perception):
                    if self.is_standing_on_food(perception):
                        return self.pickup_food()
                    else:
                        action = self._move_towards_direction(perception.direction, perception.get_food_direction())
                        if action == AntAction.MOVE_FORWARD:
                            mem["relative_pos"][0] += self.updateRelativePos(perception)[0]
                            mem["relative_pos"][1] += self.updateRelativePos(perception)[1]
                        return action
                else:
                    if len(perception.visible_cells) <= 4: # contre un mur
                        mem["knows_path"] = False
                        return self._random_move()
                    direction = self.get_direction_to_food(mem["food_pos"])
                    if direction is not None:
                        action = self._move_towards_direction(perception.direction, direction)
                        if action == AntAction.MOVE_FORWARD:
                            mem["relative_pos"][0] += self.updateRelativePos(perception)[0]
                            mem["relative_pos"][1] += self.updateRelativePos(perception)[1]
                        return action
                    else:
                        return self._random_move()

            if self.sees_food(perception):
                if self.is_standing_on_food(perception):
                    mem["food_pos"][0] = mem["relative_pos"][0]
                    mem["food_pos"][1] = mem["relative_pos"][1]
                    mem["knows_path"] = True
                    return self.pickup_food()
                else:
                    action = self._move_towards_direction(perception.direction, perception.get_food_direction())
                    if action == AntAction.MOVE_FORWARD:
                        mem["relative_pos"][0] += self.updateRelativePos(perception)[0]
                        mem["relative_pos"][1] += self.updateRelativePos(perception)[1]
                    return action
            if len(perception.visible_cells) <= 4:
                return self.turn_right()
            else:
                action = self._random_move()
                if action == AntAction.MOVE_FORWARD:
                    mem["relative_pos"][0] += self.updateRelativePos(perception)[0]
                    mem["relative_pos"][1] += self.updateRelativePos(perception)[1]
                return action

    def updateRelativePos(self, perception):
        if perception.direction.value == 0:
            return [-1, 0]
        elif perception.direction.value == 1:
            return [-1, 1]
        elif perception.direction.value == 2:
            return [0, 1]
        elif perception.direction.value == 3:
            return [1, 1]
        elif perception.direction.value == 4:
            return [1, 0]
        elif perception.direction.value == 5:
            return [1, -1]
        elif perception.direction.value == 6:
            return [0, -1]
        elif perception.direction.value == 7:
            return [-1, -1]



    def _move_towards_direction(self, current_direction, target_direction):
        """
        Retourne l'action à effectuer pour s'orienter vers la direction cible.
        """
        if current_direction == target_direction:
            return AntAction.MOVE_FORWARD
        diff = (target_direction- current_direction.value) % 8
        if diff == 0:
            return AntAction.MOVE_FORWARD
        elif diff < 4:
            return AntAction.TURN_RIGHT
        else:
            return AntAction.TURN_LEFT

    def _random_move(self):
        """
        Effectue un mouvement aléatoire (avancer, tourner à gauche ou à droite).
        """
        return random.choice([AntAction.MOVE_FORWARD, AntAction.TURN_LEFT, AntAction.TURN_RIGHT])