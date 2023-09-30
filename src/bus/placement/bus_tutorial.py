from getter_functions import GetterFunctions
from graph_utils import Graph
from qubo import QUBO

import rustworkx as rw

if __name__ == "__main__":
    getter = GetterFunctions()
    f_list = getter.normalize(getter.pop_at_station)
    g_list = getter.normalize(getter.distance_from_metro)
    h_list = getter.normalize(getter.delay_from_station)
    graph = Graph(getter.coordinates, getter.selected_coordinates, getter.station_distances)
    
    # get the betweenness centrality of the graph
    bw_centrality = rw.betweenness_centrality(graph.graph)

    # create the QUBO
    qubo = QUBO(graph, bw_centrality)

    # solve the QUBO using simulated annealing
    neal_solution = qubo.get_neal_solution()
    print("Solution: ", neal_solution)

    # save the solution to a json file
    qubo.save_solution_to_json(getter.coordinates, neal_solution, "./data/solution.json")

    # create problem for qaoa
    qp = qubo.create_problem()

    # solve the QUBO using qaoa
    qaoa_solution = qubo.run_qaoa(qp)
    print("QAOA Solution: ", qaoa_solution)

    # solve the QUBO using exact solver
    exact_solution = qubo.run_exact(qp)
    print("Exact Solution: ", exact_solution)