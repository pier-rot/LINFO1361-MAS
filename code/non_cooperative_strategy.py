import random
from environment import TerrainType
from ant import AntAction, AntStrategy
from common import Direction, AntPerception

class NonCooperativeStrategy(AntStrategy):
    """
    Stratégie non coopérative : chaque fourmi agit pour maximiser sa propre collecte de nourriture,
    sans coordination avec les autres. Elle ne tient pas compte des phéromones déposées par d'autres.
    """

    def decide_action(self, perception: AntPerception) -> AntAction:
        if not perception.has_food:
            if perception.can_see_food:
                print("¨Perception visible cells: ", perception.visible_cells)
                # 1. Ramasser la nourriture si la case courante est de la nourriture
                if perception.visible_cells[(0, 0)] == TerrainType.FOOD:
                    return AntAction.PICK_UP_FOOD
                else:
                    ant_direction = perception._get_direction_from_delta(0, 0)
                    if perception.get_food_direction() is not None:
                        # 2. Se déplacer vers la direction de la nourriture
                        return self._move_towards_direction(ant_direction, perception.get_food_direction())
                    return self._random_move()
            else:
                return self._random_move()
        else:
            if perception.can_see_colony:
                if perception.visible_cells[(0, 0)] == TerrainType.COLONY:
                    return AntAction.DROP_FOOD
                else:
                    ant_direction = perception._get_direction_from_delta(0, 0)
                    if perception.get_colony_direction() is not None:
                        # 3. Se déplacer vers la direction de la colonie
                        return self._move_towards_direction(ant_direction, perception.get_colony_direction())
                    return self._random_move()
            else: 
                return self._random_move()


    def _move_towards_direction(self, current_direction, target_direction):
        """
        Retourne l'action à effectuer pour s'orienter vers la direction cible.
        """
        if current_direction == target_direction:
            return AntAction.MOVE_FORWARD
        diff = (target_direction - current_direction) % 8
        if diff == 1 or diff > 4:
            return AntAction.TURN_RIGHT
        else:
            return AntAction.TURN_LEFT

    def _random_move(self):
        """
        Effectue un mouvement aléatoire (avancer, tourner à gauche ou à droite).
        """
        return random.choice([AntAction.MOVE_FORWARD, AntAction.TURN_LEFT, AntAction.TURN_RIGHT])