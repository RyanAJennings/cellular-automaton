from resource import Resource
from agent import Agent


# Print the environment. For debugging use.
def print_environment(universe):
    for i in range(universe.env_size):
        for j in range(universe.env_size):
            if isinstance(universe.environment[i][j], Agent):
                print(universe.environment[i][j].get_id(), " ", end='')
            elif isinstance(universe.environment[i][j], Resource):
                print("R  ", end='')
            else:
                print(universe.environment[i][j], " ", end='')
        print()
    print()
    print("---------------------------------------------------------")
    print()