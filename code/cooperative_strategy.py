import random
from ant import AntAction, AntStrategy
from common import TerrainType, AntPerception

class CooperativeStrategy(AntStrategy):

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
                "nSteps": 0
            }

        mem = self.memory[ant_id]    
        mem["nSteps"] += 1

        # Déposer un phéromone une fois sur trois seulement
        should_deposit = (mem["nSteps"] % 3 == 0)
         
        if self.has_food(perception):
            if should_deposit and perception.home_pheromone.get((0,0), 0) < 50:
                return AntAction.DEPOSIT_FOOD_PHEROMONE
            if self.sees_colony(perception):
                if self.is_standing_on_colony(perception):
                    mem["nSteps"] = 0
                    return self.drop_food()
                else:
                    return self._move_towards_direction(perception.direction, perception.get_colony_direction())
            if len(perception.home_pheromone) > 0:
                best = max(perception.home_pheromone.items(), key=lambda x: x[1] if x[0] != (0,0) else -1)
                if best[1] > 0:
                    direction = AntPerception._get_direction_from_delta(perception, *best[0])
                    return self._move_towards_direction(perception.direction, direction)
            if len(perception.visible_cells) <= 4:
                return self.turn_right()
            # Sinon, mouvement aléatoire
            return self._random_move()
        else :
            # Déposer un phéromone FOOD en cherchant la nourriture
            if should_deposit and perception.food_pheromone.get((0,0), 0) < 50:
                return AntAction.DEPOSIT_HOME_PHEROMONE
            if self.sees_food(perception):
                if self.is_standing_on_food(perception):
                    mem["nSteps"] = 0
                    return self.pickup_food()
                else:
                    return self._move_towards_direction(perception.direction, perception.get_food_direction())
            if len(perception.food_pheromone) > 0:
                best = max(perception.food_pheromone.items(), key=lambda x: x[1] if x[0] != (0,0) else -1)
                if best[1] > 0:
                    direction = AntPerception._get_direction_from_delta(perception, *best[0])
                    return self._move_towards_direction(perception.direction, direction)
            if len(perception.visible_cells) <= 4:
                return self.turn_right()
            return self._random_move()

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
        
    def move_towards_pheromones(self, current_direction, pos):
        x, y = pos[0], pos[1]        
        directions = {
            (-2, 2): AntAction.TURN_LEFT,   # NORTH
            (-1, 1): AntAction.TURN_LEFT,   # NORTHEAST
            (-1, 2): AntAction.TURN_LEFT,    # EAST
            (0, 1): AntAction.MOVE_FORWARD,    # SOUTHEAST
            (0, 2): AntAction.MOVE_FORWARD,    # SOUTH
            (0, 3): AntAction.MOVE_FORWARD,   # SOUTHWEST
            (1, 1): AntAction.TURN_RIGHT,   # WEST
            (1, 2): AntAction.TURN_RIGHT,   # NORTHWEST
            (2, 2): AntAction.TURN_RIGHT   # NORTHWEST
        }
        return directions[(x,y)]
    

    def _random_move(self):
        """
        Effectue un mouvement aléatoire (avancer, tourner à gauche ou à droite).
        """
        return random.choice([AntAction.MOVE_FORWARD, AntAction.TURN_LEFT, AntAction.TURN_RIGHT])
    def _random_move_home(self):
        """
        Effectue un mouvement aléatoire (avancer, tourner à gauche ou à droite).
        """
        return random.choice([AntAction.MOVE_FORWARD, AntAction.TURN_LEFT, AntAction.TURN_RIGHT, AntAction.DEPOSIT_HOME_PHEROMONE])
    def _random_move_food(self):
        """
        Effectue un mouvement aléatoire (avancer, tourner à gauche ou à droite).
        """
        return random.choice([AntAction.MOVE_FORWARD, AntAction.TURN_LEFT, AntAction.TURN_RIGHT, AntAction.DEPOSIT_FOOD_PHEROMONE])