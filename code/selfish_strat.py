from ant import *
from environment import TerrainType
from collections import deque
import random

class SelfishStrategy(AntStrategy):
    def __init__(self):
        self.exploration_logs = {}
    def decide_action(self, perception : AntPerception) -> AntAction:
        
        ant_id = perception.ant_id
        if perception.steps_taken == 0:
            self.exploration_logs[ant_id] = deque()

        if (
            not perception.has_food
            and (0, 0) in perception.visible_cells
            and perception.visible_cells[(0, 0)] == TerrainType.FOOD
        ):
            for i in range(4):
                self.exploration_logs[ant_id].append(AntAction.TURN_LEFT)
            return AntAction.PICK_UP_FOOD
        
        if (
            perception.has_food
            and TerrainType.COLONY in perception.visible_cells.values()
        ):
            for pos, terrain in perception.visible_cells.items():
                if terrain == TerrainType.COLONY:
                    if pos == (0, 0):
                        self.exploration_logs[ant_id] = deque()
                        for i in range(4):
                            self.exploration_logs[ant_id].append(AntAction.TURN_LEFT)
                        return AntAction.DROP_FOOD
                    
        action = self._decide_movement(perception)
        if not perception.has_food:
            self.exploration_logs[ant_id].append(action)
        return action
    
    
    def _decide_movement(self, perception : AntPerception) -> AntAction:

        if perception.has_food:
            if perception.can_see_colony():
                col_dir = perception.get_colony_direction()
                if (perception.direction.value - col_dir) == 0:
                    return AntAction.MOVE_FORWARD
                elif (perception.direction.value - col_dir) % 8 > 4:
                    return AntAction.TURN_RIGHT
                elif (perception.direction.value - col_dir) % 8 <= 4:
                    return AntAction.TURN_LEFT
                
            try:
                next_action = self.exploration_logs.get(perception.ant_id).pop()
                if next_action == AntAction.TURN_LEFT:
                    return AntAction.TURN_RIGHT
                elif next_action == AntAction.TURN_RIGHT:
                    return AntAction.TURN_LEFT
                else:
                    return  AntAction.MOVE_FORWARD
            except:
                pass



            
                    
        else:
            if perception.can_see_food() and not perception.has_food:
                food_dir = perception.get_food_direction()
                if (perception.direction.value - food_dir) == 0:
                    return AntAction.MOVE_FORWARD
                elif (perception.direction.value - food_dir) % 8 > 4:
                    return AntAction.TURN_RIGHT
                elif (perception.direction.value - food_dir) % 8 <= 4:
                    return AntAction.TURN_LEFT
            
                    
        choice = random.random()

        if choice < 0.8:
            return AntAction.MOVE_FORWARD
        elif choice < 0.9:
            return AntAction.TURN_LEFT
        else:
            return AntAction.TURN_RIGHT