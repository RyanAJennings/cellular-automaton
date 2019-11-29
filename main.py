from universe import Universe
universe = Universe(2, 5, 0.4)

for i in range(1000):
    universe.update()