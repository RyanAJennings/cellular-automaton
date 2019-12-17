from resource import Resource
from agent import Agent
from randomgen import PCG64


class Universe:
    EMPTY_CELL = 0
    BARRIER_CELL = -1

    # Constructor for the simulation universe.
    # - num_agents: integer total number of agents to be spawned in the environment
    # - env_size: integer size of the environment
    # - resource_prob: the probability that, given any empty cell in the environment, 
    #   a resources resides there.
    def __init__(self, num_agents, env_size, resource_prob, metabolic_rate=1, field_of_vision=1,
                 seed=1234567, debug=False):
        self.timestep = 0
        self.agents = list()
        self.resources = list()
        self.agents_loc = dict()
        self.environment = [[self.EMPTY_CELL for x in range(env_size)] for y in range(env_size)]
        self.env_size = env_size
        self.debug = debug
        
        # Keep track of agents that have been eliminated in the current turn to remove them from the universe
        self.agents_to_remove = []

        # Four streams:
        # 0. To place agents randomly in the environment
        # 1. To determine strategy value for each agent
        # 2. To determine whether a cell is a resource cell
        # 3. To shuffle the list of agents
        self.streams = [PCG64(seed, stream) for stream in range(4)]

        # Place agents randomly in the environment
        for i in range(num_agents):
            rand_start_x = self.streams[0].generator.randint(0, env_size-1, closed=True)
            rand_start_y = self.streams[0].generator.randint(0, env_size-1, closed=True)
            while self.environment[rand_start_x][rand_start_y] != self.EMPTY_CELL:
                rand_start_x = self.streams[0].generator.randint(0, env_size-1, closed=True)
                rand_start_y = self.streams[0].generator.randint(0, env_size-1, closed=True)

            self.agents.append(Agent(id=i+1, fov_radius=field_of_vision, resources=10, metabolic_rate=metabolic_rate,
                                     strategy=self.get_random_strategy(), seed=i))

            self.agents_loc[self.agents[i]] = (rand_start_x, rand_start_y)
            self.environment[rand_start_x][rand_start_y] = self.agents[i]
        
        # Place resources randomly
        for i in range(env_size):
            for j in range(env_size):
                # If an agent has already been placed here
                if self.environment[i][j] != self.EMPTY_CELL:
                    continue
                # With probability resource_prob, place a resource in this cell
                if self.streams[2].generator.uniform(0, 1) < resource_prob:
                    self.resources.append(Resource(10))
                    self.environment[i][j] = self.resources[-1]

    def get_random_strategy(self):
        strategy = self.streams[1].generator.normal(loc=0.0, scale=5.0)
        strategy = int(round(strategy))
        if strategy < -10:
            strategy = -10
        if strategy > 10:
            strategy = 10
        return strategy

    def is_finished(self):
        if len(self.agents) == 1:
            return True
        return False

    # Updates the agents and resources in the environment
    def update(self, stats):
        if self.timestep == 0:
            stats.set_agents(self.agents)
        self.timestep += 1

        # Move the agents in a random order
        self.streams[3].generator.shuffle(self.agents)
        for agent in self.agents:
            # If this agent was eliminated by another agent in this timestep
            if agent in self.agents_to_remove:
                continue
            
            # Update the agents resources based on the agents metabolic rate
            if agent.update_resources() <= 0:
                self.agents_to_remove.append(agent)
                loc_x, loc_y = self.agents_loc[agent]
                self.environment[loc_x][loc_y] = self.EMPTY_CELL
                continue

            # Allow the agent to strategically determine its desired move
            # This should be one of [(0,0), (-1, 0), (1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
            move_x, move_y = agent.find_best_move(self.find_restricted_env(agent))
            
            # If the agent chose to remain in the current space, no further update required
            if move_x == 0 and move_y == 0:
                continue
            
            # Get the agents current location
            old_loc_x, old_loc_y = self.agents_loc[agent]
            # Consistency check
            if self.debug and self.environment[old_loc_x][old_loc_y] != agent:
                print("Agent location does not match environment!")

            # Resolve the movement of the agent to the new location
            self.resolve_movement(old_loc_x, old_loc_y, old_loc_x + move_x, old_loc_y + move_y)

        stats.update(False, self.timestep, self.agents_to_remove)

        # Remove eliminated agents
        for agent in self.agents_to_remove:
            agent.set_time_alive(self.timestep)  # Update the agents time alive
            self.agents.remove(agent)
            del self.agents_loc[agent]
            # If one agent is left, stop removing, remaining agent is the winner
            if len(self.agents) == 1:
                break
        self.agents_to_remove = []

        if self.is_finished():
            for agent in self.agents:
                agent.set_time_alive(self.timestep+1) # Record the winning agents time alive
            stats.update(True, self.timestep+1, [])
            if self.debug:
                print("Simulation has ended. Agent", self.agents[0].get_id(), "has won!")
            return

    # Resolves the movement of an agent from its current location to a new location
    def resolve_movement(self, old_x, old_y, new_x, new_y):
        if self.debug:
            print("Agent", self.environment[old_x][old_y].get_id(),
                  "wants to move from (", old_x, ",", old_y, ") to (", new_x, ",", new_y, ")")

        # If the agent intends to stay in place
        if old_x == new_x and old_y == new_y:
            return

        old_cell = self.environment[old_x][old_y]
        new_cell = self.environment[new_x][new_y]
        
        if not isinstance(old_cell, Agent):
            if self.debug:
                print("Error: old_cell not agent!")
            print(old_x, ",", old_y) 

        # If the agent is moving to attack another agent
        if isinstance(new_cell, Agent):
            self.environment[new_x][new_y] = self.resolve_agent_collision(old_cell, new_cell, new_x, new_y)

        # If the agent is moving to collect a resource
        elif isinstance(new_cell, Resource):
            self.resolve_resource_collision(old_cell, new_cell, new_x, new_y)

        # If the agent is moving into an empty cell
        else:
            if self.debug and self.environment[new_x][new_y] != self.EMPTY_CELL:
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
            if self.debug:
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
            if self.debug:
                print("Agent", agent_2.get_id(), "killed Agent", agent_1.get_id())
            return agent_2  # Return the winner

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
                if self.is_valid_position(x-i, y-j):
                    restricted_env[fov-i][fov-j] = self.environment[x-i][y-j] 
                else:
                    restricted_env[fov-i][fov-j] =  self.BARRIER_CELL

                if self.is_valid_position(x-i, y+j):
                    restricted_env[fov-i][fov+j] = self.environment[x-i][y+j] 
                else:
                    restricted_env[fov-i][fov+j] =  self.BARRIER_CELL

                if self.is_valid_position(x+i, y+j):
                    restricted_env[fov+i][fov+j] = self.environment[x+i][y+j] 
                else:
                    restricted_env[fov+i][fov+j] =  self.BARRIER_CELL

                if self.is_valid_position(x+i, y-j):
                    restricted_env[fov+i][fov-j] = self.environment[x+i][y-j] 
                else:
                    restricted_env[fov+i][fov-j] =  self.BARRIER_CELL

        return restricted_env

    # Check if the given coordinates are within the bounds environment
    def is_valid_position(self, i, j):
        return i >= 0 and i < self.env_size and j >=0  and j < self.env_size
