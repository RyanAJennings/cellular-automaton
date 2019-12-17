from universe import Universe
from agent import Agent
from util import print_environment
from statistics import Statistics


def test_single_agent():
    print("### test_single_agent() ###")
    universe = Universe(1, 5, 0.0, debug=False)
    counter = 0
    while not universe.is_finished():
        universe.update()
        counter += 1
    assert counter == 0


def test_two_agents():
    print("### test_two_agents() ###")
    universe = Universe(2, 5, 0.0, debug=False)
    stats = Statistics()
    counter = 0
    while not universe.is_finished():
        universe.update(stats)
        counter += 1

    assert counter <= 10


def test_simulation_run():
    print("### test_simulation_run() ###")
    universe = Universe(2, 5, 0.4, debug=True)
    stats = Statistics()
    print("Start:")
    print_environment(universe)
    print("Agent stats:")
    for agent in universe.agents:
        agent.print_stats()

    while not universe.is_finished():
        universe.update(stats)
        print_environment(universe)


def test_find_best_move():
    print("### test_find_best_move() ###")
    agent = Agent(id=1, fov_radius=1, resources=10, metabolic_rate=1, strategy=0, seed=0)
    scores = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    assert agent._find_best_move(scores) == [1, 1]

    scores = [
        [0, 0, 0],
        [0, 1, 0],
        [0, 0, 0]
    ]
    assert agent._find_best_move(scores) == [0, 0]


if __name__ == "__main__":
    test_find_best_move()
    test_single_agent()
    test_two_agents()
    test_simulation_run()
