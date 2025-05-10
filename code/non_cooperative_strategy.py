import random
from ant import AntAction, AntStrategy
from common import TerrainType, AntPerception

class NonCooperativeStrategy(AntStrategy):
    """
    Stratégie non coopérative : chaque fourmi agit pour maximiser sa propre collecte de nourriture,
    sans coordination avec les autres. Elle ne tient pas compte des phéromones déposées par d'autres.
    """

    def decide_action(self, perception: AntPerception) -> AntAction:
        if not perception.has_food:
            if TerrainType.FOOD in [cell for cell in perception.visible_cells.values()]:
                # 1. Ramasser la nourriture si la case courante est de la nourriture
                if perception.visible_cells[(0, 0)] == TerrainType.FOOD:
                    return AntAction.PICK_UP_FOOD
                else:
                   return self._move_towards_direction(perception.direction, perception.get_food_direction())
            else:
                return self._random_move()
        else:
            if TerrainType.COLONY in [cell for cell in perception.visible_cells.values()]:
                if perception.visible_cells[(0, 0)] == TerrainType.COLONY:
                    return AntAction.DROP_FOOD
                else:
                    return self._move_towards_direction(perception.direction, perception.get_colony_direction())
            else: 
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

    def _random_move(self):
        """
        Effectue un mouvement aléatoire (avancer, tourner à gauche ou à droite).
        """
        return random.choice([AntAction.MOVE_FORWARD, AntAction.TURN_LEFT, AntAction.TURN_RIGHT])