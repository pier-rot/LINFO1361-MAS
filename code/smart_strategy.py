import random
from ant import AntAction, AntStrategy
from common import TerrainType, AntPerception

class SmartStrategy(AntStrategy):

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
    
    

    def get_front_cell(self, perception):
        DIRECTION_TO_DELTA = {
            0: (0, -1),   # NORTH
            1: (1, -1),   # NORTHEAST
            2: (1, 0),    # EAST
            3: (1, 1),    # SOUTHEAST
            4: (0, 1),    # SOUTH
            5: (-1, 1),   # SOUTHWEST
            6: (-1, 0),   # WEST
            7: (-1, -1),  # NORTHWEST
        }
        dx, dy = DIRECTION_TO_DELTA[perception.direction.value]
        return perception.visible_cells.get((dx, dy), None)
        
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
    

    def decide_action(self, perception: AntPerception) -> AntAction: 
        ant_id = perception.ant_id
        if ant_id not in self.memory:
            self.memory[ant_id] = {
                "food_pos": [0, 0],
                "colony_pos": [0,0],
                "relative_pos": [0,0],
                "blocked": False
            }

        mem = self.memory[ant_id]


        # Déposer un phéromone une fois sur quatre seulement
        should_deposit = (perception.steps_taken % 3 == 0)

        if mem["blocked"]:
            if self.get_front_cell(perception) == TerrainType.WALL or len(perception.visible_cells) <= 1:
                return AntAction.TURN_RIGHT
            else:
                mem["blocked"] = False
                mem["relative_pos"][0] += self.updateRelativePos(perception)[0]
                mem["relative_pos"][1] += self.updateRelativePos(perception)[1]
                return AntAction.MOVE_FORWARD
         
        # --- Porte de la nourriture --- #
        if self.has_food(perception):
            # Dépôt intelligent de phéromone FOOD
            if should_deposit and perception.food_pheromone.get((0,0), 0) < 50:
                return AntAction.DEPOSIT_FOOD_PHEROMONE
            
            # Si la colonie est visible, priorité vers celle-ci
            if self.sees_colony(perception):
                if self.is_standing_on_colony(perception):
                    mem["relative_pos"] = [0,0]
                    return self.drop_food()
                else:
                    action = self._move_towards_direction(perception, perception.direction, perception.get_colony_direction())
                    if action == AntAction.MOVE_FORWARD:
                        mem["relative_pos"][0] += self.updateRelativePos(perception)[0]
                        mem["relative_pos"][1] += self.updateRelativePos(perception)[1]
                    return action
                
            # Si bloqué, tourne à droite
            if self.get_front_cell(perception) == TerrainType.WALL or len(perception.visible_cells) <= 1:
                mem["blocked"] = True
                return AntAction.TURN_RIGHT

            # Suivre le gradient de phéromone HOME
            if len(perception.home_pheromone) > 0 :
                best = max(perception.home_pheromone.items(), key=lambda x: x[1] if x[0] != (0,0) else -1)
                if best[1] > 60:
                    direction = AntPerception._get_direction_from_delta(perception, *best[0])
                    action = self._move_towards_direction(perception, perception.direction, direction)
                    if action == AntAction.MOVE_FORWARD:
                        mem["relative_pos"][0] += self.updateRelativePos(perception)[0]
                        mem["relative_pos"][1] += self.updateRelativePos(perception)[1]
                    return action
            
            # Tenter de se diriger vers la colonie
            direction = self.get_direction_to_origin(mem["relative_pos"])
            if direction is not None:
                action = self._move_towards_direction(perception, perception.direction, direction)
                if action == AntAction.MOVE_FORWARD:
                    mem["relative_pos"][0] += self.updateRelativePos(perception)[0]
                    mem["relative_pos"][1] += self.updateRelativePos(perception)[1]
                return action
            
            # Sinon, mouvement aléatoire
            action = self._random_move(perception)
            if action == AntAction.MOVE_FORWARD:
                mem["relative_pos"][0] += self.updateRelativePos(perception)[0]
                mem["relative_pos"][1] += self.updateRelativePos(perception)[1]
            return action
        
        # --- Cherche de la nourriture --- #
        else :
            # Dépôt intelligent de phéromone HOME
            if should_deposit and perception.home_pheromone.get((0,0), 0) < 50:
                return AntAction.DEPOSIT_HOME_PHEROMONE
            
            # Si la nourriture est visible, priorité vers celle-ci
            if self.sees_food(perception):
                if self.is_standing_on_food(perception):
                    mem["food_pos"][0] = mem["relative_pos"][0]
                    mem["food_pos"][1] = mem["relative_pos"][1]
                    return self.pickup_food()
                else:
                    action = self._move_towards_direction(perception, perception.direction, perception.get_food_direction())
                    if action == AntAction.MOVE_FORWARD:
                        mem["relative_pos"][0] += self.updateRelativePos(perception)[0]
                        mem["relative_pos"][1] += self.updateRelativePos(perception)[1]
                    return action
                
            # Si bloqué, tourne
            if self.get_front_cell(perception) == TerrainType.WALL or len(perception.visible_cells) <= 1:
                mem["blocked"] = True
                return AntAction.TURN_RIGHT
                
            # Suivre le gradient de phéromone FOOD
            if len(perception.food_pheromone) > 0 :
                best = max(perception.food_pheromone.items(), key=lambda x: x[1] if x[0] != (0,0) else -1)
                if best[1] > 0:
                    direction = AntPerception._get_direction_from_delta(perception, *best[0])
                    action = self._move_towards_direction(perception, perception.direction, direction)
                    if action == AntAction.MOVE_FORWARD:
                        mem["relative_pos"][0] += self.updateRelativePos(perception)[0]
                        mem["relative_pos"][1] += self.updateRelativePos(perception)[1]
                    return action
            
            # Exploration intelligente
            action = self._random_move(perception)
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

    def _move_towards_direction(self, perception, current_direction, target_direction):
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

    def _random_move(self, perception):
        choice = random.random()
        if choice < 0.8:
            return AntAction.MOVE_FORWARD
        elif choice < 0.9:
            return AntAction.TURN_LEFT
        else:
            return AntAction.TURN_RIGHT
        