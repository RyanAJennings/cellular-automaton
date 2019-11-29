from resource import Resource
from agent import Agent
import random
from random import randrange

class Universe:
    EMPTY_CELL = 0
    BARRIER_CELL = -1

    # Constructor for the simulation universe.
    # - num_agents: integer total number of agents to be spawned in the environment
    # - env_size: integer size of the environment
    # - resource_prob: the probability that, given any empty cell in the environment, 
    #   a resources resides there.
    def __init__(self, num_agents, env_size, resource_prob):
        self.agents = list()
        self.resources = list()
        self.agents_loc = dict()
        self.environment = [[self.EMPTY_CELL for x in range(env_size)] for y in range(env_size)]
        self.env_size = env_size
        
        # Keep track of agents that have been eliminated in the current turn to remove them from the universe
        self.agents_to_remove = []

        # Place agents randomly in the environment
        for i in range(num_agents):
            rand_start_x = randrange(0, env_size-1) 
            rand_start_y = randrange(0, env_size-1)
            while (self.environment[rand_start_x][rand_start_y] != self.EMPTY_CELL):
                rand_start_x = randrange(0, env_size-1) 
                rand_start_y = randrange(0, env_size-1)
            
            # TODO vary fov_radius, metabolic_rate, strategy of each agent
            self.agents.append(Agent(id = i+1, fov_radius=1, resources=10, metabolic_rate=1, strategy = randrange(-10, 10)))

            self.agents_loc[self.agents[i]] = (rand_start_x, rand_start_y)
            self.environment[rand_start_x][rand_start_y] = self.agents[i]
        
        # Place resources randomly
        for i in range(env_size):
            for j in range(env_size):
                # If an agent has already been placed here
                if (self.environment[i][j] != self.EMPTY_CELL):
                    continue
                # With probability resource_prob, place a resource in this cell
                if (random.uniform(0,1) < resource_prob):
                    self.resources.append(Resource(10))
                    self.environment[i][j] = self.resources[-1]


    # Updates the agents and resources in the environment
    def update(self):
        self.print_environment()

        # If only one agent remains in the simulation, then trigger endgame
        if (len(self.agents) == 1): 
            print("Agent", self.agents[0].get_id(), "has won!")
            exit(0)
        
        # Move the agents in a random order
        random.shuffle(self.agents)
        for agent in self.agents:
            # If this agent was eliminated by another agent in this timestep
            if agent in self.agents_to_remove:
                continue
            
            # Update the agents resources based on the agents metabolic rate
            agent.update_resources()

            # Allow the agent to strategically determine its desired move
            # This should be one of [(0,0), (-1, 0), (1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
            move_x, move_y = agent.find_best_move(self.find_restricted_env(agent))
            
            # If the agent chose to remain in the current space, no further update required
            if (move_x == 0 and move_y == 0):
                continue
            
            # Get the agents current location
            old_loc_x, old_loc_y = self.agents_loc[agent]
            # Consistency check
            if (self.environment[old_loc_x][old_loc_y] != agent): print("Agent location does not match environment!")

            # Resolve the movement of the agent to the new location
            self.resolve_movement(old_loc_x, old_loc_y, old_loc_x + move_x, old_loc_y + move_y)

        # Remove eliminated agents
        for agent in self.agents_to_remove:
            self.agents.remove(agent)
            del self.agents_loc[agent]
        self.agents_to_remove = []

        # TODO: Regenerate resources in the environment
        # Update the resources in the environment
        #for resource in self.resources:
        #    resource.update()


    # Resolves the movement of an agent from its current location to a new location
    def resolve_movement(self, old_x, old_y, new_x, new_y):
        print("Agent", self.environment[old_x][old_y].get_id(), "wants to move from (", old_x, ",", old_y, ") to (", new_x, ",", new_y, ")")

        # If the agent intends to stay in place
        if (old_x == new_x and old_y == new_y):
            return

        old_cell = self.environment[old_x][old_y]
        new_cell = self.environment[new_x][new_y]
        
        if (not isinstance(old_cell, Agent)):
            print("Error: old_cell not agent!")
            print(old_x, ",", old_y) 

        # If the agent is moving to attack another agent
        if (isinstance(new_cell, Agent)):
            self.environment[new_x][new_y] = self.resolve_agent_collision(old_cell, new_cell, new_x, new_y)

        # If the agent is moving to collect a resource
        elif (isinstance(new_cell, Resource)):   
            self.resolve_resource_collision(old_cell, new_cell, new_x, new_y)

        # If the agent is moving into an empty cell
        else:
            if (self.environment[new_x][new_y] != self.EMPTY_CELL): 
                print("Error: new_cell is not an agent, resource, or an empty cell. (92)")
            self.agents_loc[old_cell] = (new_x, new_y)
            self.environment[new_x][new_y] = old_cell
        
        # Set the agents old location to be an empty cell
        self.environment[old_x][old_y] = self.EMPTY_CELL

    
    def resolve_agent_collision(self, agent_1, agent_2, new_x, new_y):
        # Agent 1 wins the fight
        if agent_1.get_resources() > agent_2.get_resources():
            # agent_1 consumes agent_2's resources
            agent_1.add_resources(agent_2.get_resources())
            # Update agent_1's location in the dictionary
            self.agents_loc[agent_1] = (new_x, new_y)
            # Flag agent_2 as dead
            self.agents_to_remove.append(agent_2)
            print("Agent", agent_1.get_id(), "killed Agent", agent_2.get_id())
            return agent_1 # Return winner

        # Agent 2 wins the fight
        else:
            # agent_2 consumes agent_1's resources
            agent_2.add_resources(agent_1.get_resources())
            # Update agent_1's location in the dictionary
            self.agents_loc[agent_2] = (new_x, new_y)
            # Flag agent_1 as dead
            self.agents_to_remove.append(agent_1)
            print("Agent", agent_2.get_id(), "killed Agent", agent_1.get_id())
            return agent_2 # Return the winner


    # Resolve a collision between an agent and a resource cell
    def resolve_resource_collision(self, agent, resource, new_x, new_y):
        agent.add_resources(resource.get_amount())
        self.resources.remove(resource)
        self.agents_loc[agent] = (new_x, new_y)
        self.environment[new_x][new_y] = agent


    # Given an agent, return its field of vision in the environment based on the agents fov radius
    def find_restricted_env(self, agent):
        fov = agent.get_field_of_vision()
        x, y = self.agents_loc[agent]
        restricted_env = [[self.EMPTY_CELL for x in range(2*fov+1)] for y in range(2*fov+1)]

        # Copy the contents of the environment within the agent's fov radius into a restricted environment
        for i in range(0, fov+1):
            for j in range(0, fov+1):
                if (self.is_valid_position(x-i, y-j)):
                    restricted_env[fov-i][fov-j] = self.environment[x-i][y-j] 
                else:
                    restricted_env[fov-i][fov-j] =  self.BARRIER_CELL

                if (self.is_valid_position(x-i, y+j)):
                    restricted_env[fov-i][fov+j] = self.environment[x-i][y+j] 
                else:
                    restricted_env[fov-i][fov+j] =  self.BARRIER_CELL

                if (self.is_valid_position(x+i, y+j)):
                    restricted_env[fov+i][fov+j] = self.environment[x+i][y+j] 
                else:
                    restricted_env[fov+i][fov+j] =  self.BARRIER_CELL

                if (self.is_valid_position(x+i, y-j)):
                    restricted_env[fov+i][fov-j] = self.environment[x+i][y-j] 
                else:
                    restricted_env[fov+i][fov-j] =  self.BARRIER_CELL

        return restricted_env


    # Check if the given coordinates are within the bounds environment
    def is_valid_position(self, i, j):
        return i >= 0 and i < self.env_size and j >=0  and j < self.env_size


    # Print the environment. For debugging use.
    def print_environment(self):
        for i in range(self.env_size):
            for j in range(self.env_size):
                if (isinstance(self.environment[i][j], Agent)):
                    print(self.environment[i][j].get_id(), " ", end='')
                elif (isinstance(self.environment[i][j], Resource)):
                    print("R  ", end='')
                else:
                    print(self.environment[i][j], " ", end='')
            print()
        print()
        print("---------------------------------------------------------")
        print()
                

        
        
        
        




