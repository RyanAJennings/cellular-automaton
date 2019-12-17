import math
from resource import Resource
from randomgen import PCG64

EMPTY_CELL = 0
BARRIER_CELL = -1


class Agent:
    # Constructor for an Agent.
    # - id: unique identifier for this agent
    # - fov_radius: agent's field of view; integer radius around the agent's cell 
    #   that the agent is able to view
    # - resources: the amount of resources that the agent begins with
    # - metabolic_rate: how many resources the agent loses per move
    # - strategy: ranges from [-10, 10] where -10 is the most defensive and 10 is 
    #   the most aggressive
    def __init__(self, id, fov_radius, resources, metabolic_rate, strategy, seed):
        self.id = id
        self.fov_radius = fov_radius
        self.resources = resources
        self.metabolic_rate = metabolic_rate
        if strategy < -10 or strategy > 10:
            print("Error: unexpected strategy value. Expected [-10, 10]")
        self.strategy = strategy
        self.generator = PCG64(seed, 0).generator
        self.time_alive = 0

    # Returns the best movement decision for the Agent based on the given environment 
    # and the agent's field of vision
    def find_best_move(self, environment):
        agents = []     # Agents in the given environment
        resources = []  # Resources in the given environment
        fov_radius = self.fov_radius

        # Scores for each cell in the environment corresponding to the relative 
        # advantage/disadvantage of moving to that cell. The higher the score, the 
        # better an option it is.
        scores = [[0 for x in range(2*fov_radius + 1)] for y in range(2*fov_radius + 1)]

        # Populate <agents> and <resources>
        for i in range(2*fov_radius + 1):
            for j in range(2*fov_radius + 1):
                if i == fov_radius and j == fov_radius:
                    continue
                if isinstance(environment[i][j], Agent):
                    agents.append(((i,j), environment[i][j]))
                if isinstance(environment[i][j], Resource):
                    resources.append(((i,j), environment[i][j]))
        
        # Score each cell in the environment based on its distance to 
        for i in range(2*fov_radius + 1):
            for j in range(2*fov_radius + 1):
                if  environment[i][j] == BARRIER_CELL:
                    scores[i][j] = -math.inf
                    continue

                # Adjust the scores based on the cells manhattan distance to an agent
                if self.strategy != 0:
                    for (x, y), agent in agents:
                        distance = max(abs(x-i), abs(y-j)) # Manhattan distance with sloped movement
                        # More aggressive agents will score movement toward agents higher than more defensive agents
                        scores[i][j] += self.strategy + distance if self.strategy < 0 else self.strategy - distance

                # Adjust the scores based on the cells manhattan distance to a resource
                for (x, y), resource in resources:
                    distance = max(abs(x-i), abs(y-j)) # Manhattan distance with sloped movement
                    scores[i][j] += resource.get_amount() - distance

        return self._find_best_move(scores) 

    # Finds the best move among a grid of scores. If multiple cells contain the best score, a 
    # random cell will be chosen and returned among these cells.
    def _find_best_move(self, scores):
        fov_radius = self.fov_radius

        # Agents move one cell per turn
        moves = [(0, 0), (-1, 0), (-1, 1), (-1, -1), (0, 1), (0, -1), (1, -1), (1, 1)]

        # Keep track of the best possible score and the moves that result in them
        best_score = -math.inf
        best_moves = list(moves)

        for (move_x, move_y) in moves:
            if scores[fov_radius+move_x][fov_radius+move_y] > best_score:
                best_score = scores[fov_radius+move_x][fov_radius+move_y]
                best_moves = [(move_x, move_y)]
            elif scores[fov_radius+move_x][fov_radius+move_y] == best_score:
                best_moves.append((move_x, move_y))

        # Consistency check
        if best_score == -math.inf:
            print("Error: barrier block chosen in _find_best_move!")

        return self.generator.choice(best_moves).tolist()
    
    def die(self, time):
        self.time_alive = time

    # Return the number of resources that the agent currently has
    def get_resources(self):
        return self.resources

    # Add a given number of resources to the agents resource collection
    def add_resources(self, amount):
        self.resources += amount

    # Update the agents resources for a single turn
    def update_resources(self):
        self.resources -= self.metabolic_rate
        return self.resources

    # Return the unique identifier of the agent
    def get_id(self):
        return self.id

    # Returns the agent's field of vision
    def get_field_of_vision(self):
        return self.fov_radius

    def print_stats(self):
        print("Agent ", self.id)
        print("\tField of vision    :", self.fov_radius)
        print("\tResources          :", self.resources)
        print("\tMetabolic rate     :", self.metabolic_rate)
        print("\tStrategy           :", self.strategy)
