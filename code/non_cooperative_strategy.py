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
    

    def decide_action(self, perception: AntPerception) -> AntAction:
        ant_id = perception.ant_id
        if ant_id not in self.memory:
            self.memory[ant_id] = {
                "path": [],
                "init_direction": perception.direction.value,
                "food_direction": None,
                "wall": False
            }

        mem = self.memory[ant_id]

        if self.has_food(perception) or mem["wall"]:
            if self.sees_colony(perception):
                if self.is_standing_on_colony(perception):
                    if self.has_food(perception):
                        return self.drop_food()
                    else:
                        mem["init_direction"] = (mem["init_direction"] + 1) % 8
                        mem["wall"] = False
                        return self.turn_right()
                else:
                    return self._move_towards_direction(perception.direction, perception.get_colony_direction())
            if self.is_in_the_opposite_direction(perception, mem["init_direction"]):
                return self.move_forward()
            else:
                return self.turn_right()
        else :
            if mem["food_direction"]:
                if not self.is_in_the_same_direction(perception, mem["food_direction"]):
                    return self.turn_right()
            if self.sees_food(perception):
                if self.is_standing_on_food(perception):
                    mem["food_direction"] = perception.direction.value
                    print(mem["food_direction"])
                    return self.pickup_food()
                else:
                    return self._move_towards_direction(perception.direction, perception.get_food_direction())
            if len(perception.visible_cells) <= 4:
                mem["wall"] = True
                return self.turn_right()
            else:
                return self.move_forward()


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