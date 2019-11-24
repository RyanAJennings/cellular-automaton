from resource import Resource
from agent import Agent
import random
from random import randrange

class Universe:
    EMPTY_CELL = 0
    BARRIER_CELL = -1

    def __init__(self, num_agents, env_size, resource_prob):
        self.agents = list()
        self.resources = list()
        self.agents_loc = dict()
        self.environment = [[self.EMPTY_CELL]*env_size]*env_size
        self.env_size = env_size
        self.agents_to_remove = []

        # Place agents randomly
        for i in range(num_agents):
            rand_start_x = randrange(0, env_size-1) 
            rand_start_y = randrange(0, env_size-1)
            while (self.environment[rand_start_x][rand_start_y] != self.EMPTY_CELL):
                rand_start_x = randrange(0, env_size-1) 
                rand_start_y = randrange(0, env_size-1)
            self.agents.append(Agent(fov_radius=1, resources=10, metabolic_rate=1, strategy = randrange(-10, 10)))
            self.agents_loc[self.agents[i]] = (rand_start_x, rand_start_y)
            self.environment[rand_start_x][rand_start_y] = self.agents[i]
        
        # Place resources randomly
        for i in range(env_size):
            for j in range(env_size):
                if(self.environment != self.EMPTY_CELL):
                    continue
                if (random.uniform(0,1) < resource_prob):
                    self.resources.append(Resource(10))
                    environment[i][j] = self.resources[-1]

    def update(self):
        random.shuffle(self.agents)
        for agent in self.agents:
            if agent in self.agents_to_remove:
                continue
            move_x, move_y = agent.find_best_move(self.find_restricted_env(agent))
            old_loc_x, old_loc_y = self.agents_loc[agent]
            self.resolve_movement(old_loc_x, old_loc_y, old_loc_x + move_x, old_loc_y + move_y)
        for agent in self.agents_to_remove:
            self.agents.remove(agent)
            del self.agents_loc[agent]
        self.agents_to_remove = []
        for resource in self.resources:
            resource.update()

    def resolve_movement(self, old_x, old_y, new_x, new_y):
        old_cell = self.environment[old_x][old_y]
        new_cell = self.environment[new_x][new_y]
        self.environment[old_x][old_y] = self.EMPTY_CELL
        old_cell.update_resources()
        if (isinstance(new_cell, Agent)):
            self.environment[new_x][new_y] = self.resolve_agent_collision(old_cell, new_cell)
        elif (isinstance(new_cell, Resource)):
            self.environment[new_x][new_y] = old_cell
            self.resolve_resource_collision(old_cell, new_cell)
    
    def resolve_agent_collision(self, agent_1, agent_2):
        if agent_1.get_resources() > agent_2.get_resources():
            agent_1.add_resources(agent_2.get_resources())
            self.agents_to_remove.append(agent_2)
            return agent_1
        else:
            agent_2.add_resources(agent_1.get_resources())
            self.agents_to_remove.append(agent_1)
            return agent_2

    def resolve_resource_collision(self, agent, resource):
        agent.add_resources(resource.get_amount())

    def find_restricted_env(self, agent):
        fov = agent.get_field_of_vision()
        x, y = self.agents_loc[agent]
        restricted_env = [[self.EMPTY_CELL]*(2*fov+1)] * (2*fov+1)

        for i in range(1, fov+1):
            for j in range(1, fov+1):
                if (self.is_valid_position(x-i, y-j)):
                    restricted_env[i][j] = self.environment[x-i][y-j] 
                else:
                    restricted_env[i][j] =  self.BARRIER_CELL

                if (self.is_valid_position(x+i, y+j)):
                    restricted_env[i][j] = self.environment[x+i][y+j] 
                else:
                    restricted_env[i][j] =  self.BARRIER_CELL
        return restricted_env

    def is_valid_position(self, i, j):
        return i >= 0 and i < self.env_size and j >=0  and j < self.env_size

        
        
        
        




