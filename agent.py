import random
import math
from resource import Resource

class Agent:
    def __init__(self, fov_radius, resources, metabolic_rate, strategy):
        self.fov_radius = fov_radius
        self.resources = resources
        self.metabolic_rate = metabolic_rate
        self.strategy = strategy

    def get_field_of_vision(self):
        return self.fov_radius
    
    def find_best_move(self, environment):
        # Make a strategic movement decision based on the given environment
        agents = []
        resources = []
        barriers = []
        fov_radius = self.fov_radius
        scores = [[0]*(2*fov_radius + 1)]*(2*fov_radius + 1)

        for i in range(2*fov_radius + 1):
            for j in range(2*fov_radius + 1):
                if i == fov_radius and j == fov_radius:
                    continue
                if isinstance(environment[i][j], Agent):
                    agents.append(((i,j), environment[i][j]))
                if isinstance(environment[i][j], Resource):
                    resources.append(((i,j), environment[i][j]))
        
        for i in range(2*fov_radius + 1):
            for j in range(2*fov_radius + 1):
                for (x,y), agent in agents:
                    distance = max(abs(x-i), abs(y-j))
                    scores[i][j] = self.strategy + distance if self.strategy < 0 else self.strategy - distance
                for (x,y), resource in resources:
                    distance = max(abs(x-i), abs(y-j))
                    scores[i][j] = resource.get_amount() - distance
                if  environment[i][j] == BARRIER_CELL:
                    scores[i][j] = -math.inf
        
        return self._find_best_move(scores) 


    def _find_best_move(self, scores):
        current_x = self.fov_radius
        current_y = self.fov_radius
        moves = [(0,0), (-1,0), (-1,1), (-1,-1), (0,1), (0,-1), (1,-1), (1,1)]
        best_score = 0
        best_moves = list(moves)
        for (move_x, move_y) in moves:
            if scores[move_x][move_y] > best_score:
                best_score = scores[move_x][move_y]
                best_moves = [(move_x, move_y)]
            elif scores[move_x][move_y] == best_score:
                best_moves.append((move_x, move_y))
        return random.choice(best_moves)

    def get_resources(self):
        return self.resources

    def add_resources(self, amount):
        self.resources += amount

    def update_resources(self):
        self.resources -= self.metabolic_rate



                

