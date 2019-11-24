from universe import Universe
universe = Universe(100, 500, 0.4)

for i in range(1000):
    universe.update()