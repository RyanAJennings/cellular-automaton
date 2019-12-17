import copy

class Stats:
    def __init__(self):
        self.final = False  # True if the simulation has completed

        self.living_agents = list()     # Living agents in the simulation
        self.dead_agents = list()       # Agents who have died in the simulation
        self.aggressive_agents = list() # All aggressive agents that participated in the simulation
        self.defensive_agents = list()  # All defensive agents that participated in the simulation
        self.neutral_agents = list()    # All neutral agents that participated in the simulation

        self.avg_win_strategy = 0
        self.avg_win_metabolic_rate = 0
        self.avg_lifespans = [0, 0, 0]   # Average defensive, neutral, and aggressive lifespans

    
    def update(self, final, time, dead_agents):
        self.final = final
        if final:
            self.compute_statistics()
            return
        for dead_agent in dead_agents:
                self.living_agents.remove(dead_agent)
                self.dead_agents.append(dead_agent)
    
    def set_agents(self, agents):
        self.living_agents = copy.copy(agents)
        for agent in self.living_agents:
            if agent.strategy < 0:
                self.defensive_agents.append(agent)
            elif agent.strategy > 0:
                self.aggressive_agents.append(agent)
            else:
                self.neutral_agents.append(agent)
              
    
    def compute_statistics(self):
        if not self.final:
            print("Simulation must be over for winning strategy stats to be reported.")
            return
        
        # Compute avg_win_strategy and avg_win_metabolic_rate
        for agent in self.living_agents:
            self.avg_win_strategy += agent.strategy
            self.avg_win_metabolic_rate += agent.metabolic_rate
        self.avg_win_strategy = self.avg_win_strategy/len(self.living_agents)
        self.avg_win_metabolic_rate = self.avg_win_metabolic_rate/len(self.living_agents)

        # Compute avg_lifespan_aggressive, avg_lifespan_defensive, and avg_lifespan_neutra
        if len(self.defensive_agents) > 0:
            for agent in self.defensive_agents:
                self.avg_lifespans[0] += agent.time_alive
            self.avg_lifespans[0]  = self.avg_lifespans[0] /len(self.defensive_agents)
        if len(self.neutral_agents) > 0:
            for agent in self.neutral_agents:
                self.avg_lifespans[1] += agent.time_alive
            self.avg_lifespans[1] = self.avg_lifespans[1]/len(self.neutral_agents)
        if len(self.aggressive_agents) > 0:
            for agent in self.aggressive_agents:
                self.avg_lifespans[2] += agent.time_alive
            self.avg_lifespans[2] = self.avg_lifespans[2]/len(self.aggressive_agents)



    def print(self):
        print("--------------------------------")
        print("Simulation Statistics")
        print("(Average) Strategy of Winning Agent(s):", self.avg_win_strategy)
        print("(Average) Metabolic Rate of Winning Agent(s):", self.avg_win_metabolic_rate)
        print("Avg Defensive Agent Lifespan:", self.avg_lifespans[0])
        print("Avg Neutral Agent Lifespan:", self.avg_lifespans[1])
        print("Avg Aggressive Agent Lifespan:", self.avg_lifespans[2])
        print("--------------------------------")
        
