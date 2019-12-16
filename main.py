from universe import Universe
from util import print_environment

universe = Universe(2, 5, 0.4)

for i in range(1000):
    print_environment(universe)
    universe.update()
