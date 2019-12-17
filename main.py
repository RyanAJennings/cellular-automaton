from statistics import Statistics
from universe import Universe
from util import print_environment

universe = Universe(2, 5, 0.4, debug=True)
print("Start:")
print_environment(universe)
print("Agent stats:")
for agent in universe.agents:
    agent.print_stats()

stats = Statistics()
while not universe.is_finished():
    universe.update(stats)
    print_environment(universe)
stats.print()
