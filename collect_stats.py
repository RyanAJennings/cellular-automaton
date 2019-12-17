from universe import Universe
from statistics import Statistics

# The simulation allows various values to be changed.
# To avoid trying to explore the full variable space,
# we decided to change variables one at a time, while
# keeping all the others at their default values.
# Thus, we collected the number of times a strategy has
# won over 10,000 simulation runs

default_values = {
    "num_agents": 100,
    "env_size": 30,
    "resource_prob": 0.4,
    "seed": 1234567,
    "metabolic_rate": 1,
    "field_of_vision": 1
}


def printWinCountsToFile(win_counts_list, toVary):
    with open("output/" + toVary + ".txt", "w") as file:
        for win_counts in win_counts_list:
            file.write(" ".join([str(i) for i in win_counts]))
            file.write("\n")
        file.close()


def collect_stats(toVary, values, args, N=100):
    win_counts_list = []
    for j in range(len(values)):
        print("\tSimulating", toVary, "=", values[j])
        args[toVary] = values[j]
        win_counts = [0 for i in range(21)]
        for i in range(N):
            stats = Statistics()
            universe = Universe(num_agents=args["num_agents"], env_size=args["env_size"],
                                resource_prob=args["resource_prob"], metabolic_rate=args["metabolic_rate"],
                                field_of_vision=args["field_of_vision"], seed=i, debug=False)
            while not universe.is_finished():
                universe.update(stats)
            win_counts[int(stats.avg_win_strategy)+10] += 1

        win_counts_list.append(win_counts)
    return win_counts_list


# # Number of agents: With respect to environment size, from 5% to 70%
# print("Varying number of agents: With respect to environment size, from 5% to 70%")
# values = [int(30*30*(i+1)*0.05) for i in range(14)]
# win_counts_list = collect_stats(toVary="num_agents", values=values, args=default_values)
# printWinCountsToFile(win_counts_list, "num_agents")
#
#
# # Resource abundance: Controlled by resource_prob variable from 0.1 to 0.9
# print("Varying resource abundance: Controlled by resource_prob variable from 0.1 to 0.9")
# values = [(i+1)*0.1 for i in range(9)]
# win_counts_list = collect_stats(toVary="resource_prob", values=values, args=default_values)
# printWinCountsToFile(win_counts_list, "resource_prob")


# Field of vision: Varying from 1 to 5
print("Varying field of vision: varying from 1 to 5")
values = [i + 1 for i in range(5)]
win_counts_list = collect_stats(toVary="field_of_vision", values=values, args=default_values)
printWinCountsToFile(win_counts_list, "field_of_vision")


# # Metabolic rate: Varying from 1 to 10
# print("Varying metabolic rate: Varying from 1 to 10")
# values = [i + 1 for i in range(10)]
# win_counts_list = collect_stats(toVary="metabolic_rate", values=values, args=default_values)
# printWinCountsToFile(win_counts_list, "metabolic_rate")
