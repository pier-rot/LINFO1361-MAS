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

    def decide_action(self, perception: AntPerception) -> AntAction:
        ant_id = perception.ant_id
        if ant_id not in self.memory:
            self.memory[ant_id] = {
                "path": [],
                "returning": False,
                "init_direction": perception.direction.value
            }

        mem = self.memory[ant_id]

        if not perception.has_food:
            if TerrainType.FOOD in [cell for cell in perception.visible_cells.values()]:
                # 1. Ramasser la nourriture si la case courante est de la nourriture
                if perception.visible_cells[(0, 0)] == TerrainType.FOOD:
                    return AntAction.PICK_UP_FOOD
                else:
                   action = self._move_towards_direction(perception.direction, perception.get_food_direction())
                   mem["path"].append(action)
                   return action
            else:
                #print(len(perception.visible_cells))
                if len(perception.visible_cells) <= 10:
                    action = AntAction.TURN_RIGHT
                    mem["path"].append(AntAction.TURN_LEFT)
                else:
                    action = AntAction.MOVE_FORWARD
                    mem["path"].append(action)
                return action
        else:
            mem["returning"] = True
            if TerrainType.COLONY in [cell for cell in perception.visible_cells.values()]:
                if perception.visible_cells[(0, 0)] == TerrainType.COLONY:
                    mem["path"] = []
                    mem["returning"] = False
                    mem["init_direction"] = perception.direction.value
                    return AntAction.DROP_FOOD
                else:
                    return self._move_towards_direction(perception.direction, perception.get_colony_direction())
            else: 
                if mem["path"]:
                    if perception.direction.value == (mem["init_direction"] + 4) % 8:
                        last_move = mem["path"].pop()
                        return last_move
                    else :
                        return AntAction.TURN_RIGHT
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