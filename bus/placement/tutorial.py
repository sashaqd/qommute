import random

import rustworkx
import matplotlib.pyplot as plt
from rustworkx.visualization import mpl_draw

from getter_functions import get_bus_station_location, select_bus_station, get_station_distance
from graph_utils import make_node_edge, make_graph
from qubo import QUBOPlacement

# Step 1: Get the bus station locations
coordinates = get_bus_station_location("./data/bus_station_location.csv")
selected_coordinates = select_bus_station(coordinates)

# select 20 random bus stations
random.seed(42)
selected_coordinates = dict(random.sample(list(selected_coordinates.items()), 20))


# Step 2: Get the distance between the bus stations
station_distance = get_station_distance("./data/station_distance.csv")

# Step 3: Make a graph from the bus stations
node_dic, index_dic, edge_dic = make_node_edge(selected_coordinates, station_distance)
graph = make_graph(node_dic, index_dic, edge_dic)

# Step 4: Compute the betweenness centrality of the graph
bw_centrality = rustworkx.betweenness_centrality(graph)
# # Create a larger figure with a specified size (adjust the values as needed)
# fig = plt.figure(figsize=(50, 50))

# # Create a subplot within the larger figure
# subax1 = plt.subplot(121)

# # Now, you can draw your graph with_labels=True on the larger subplot
# mpl_draw(graph, with_labels=True, ax=subax1)

# # Show the plot
# plt.show()

# Step 5: Get the QUBO coefficients
qubo = QUBOPlacement(graph, bw_centrality)
qubo_form, offset, model, index_dic = qubo.get_qubo()

# Step 6: Get the best sample
best_sample = qubo.get_best_sample(model, index_dic)
print("Printing best sample:")
print(best_sample)

# Step 7: Run a simulation with QAOA and also the exact solver
qaoa_result = qubo.run_qaoa(qubo_form, node_dic)
exact_result = qubo.run_exact(qubo_form, node_dic)

# ---------------------------------------------------------------------------------------------
# Running in IBMQ hardware
# from qiskit.utils import QuantumInstance

# start = time.time()
# algorithm_globals.random_seed = 10598
# qi = QuantumInstance(
#                 backend=provider.get_backend('ibm_brisbane'),
#                 seed_simulator=algorithm_globals.random_seed,
#                 seed_transpiler=algorithm_globals.random_seed,
#             )
# qaoa_mes = QAOA(optimizer=COBYLA(), initial_point=[0.0, 0.0], quantum_instance=qi)
# qaoa = MinimumEigenOptimizer(qaoa_mes)  # using QAOA
# qaoa_result = qaoa.solve(qubo)
# print(qaoa_result.prettyprint())

# print("Q Time: ", time.time() - start)
# ---------------------------------------------------------------------------------------------

# Step 8: Print the results
print("Printing QAOA result:")
print(qaoa_result.pretty_print())
print("Printing exact result:")
print(exact_result.pretty_print())

# Step 9: Save the results for the routing problem
# extract the node information from the best sample
selected_nodes = []
index = 0
for key, value in best_sample.sample.items():
  if value == 1:
    selected_nodes.append(index)
  index += 1

# extracting the name and coordinates of the selected nodes into a dictionary then to a json file
selected_nodes_dic = {"depots": []}
for i in selected_nodes:
   for key, value in index_dic.items():
      if value == i:
        selected_nodes_dic["depots"].append({"lat": coordinates[key][0], "lon": coordinates[key][1]})


import json
with open('../routing/bus_depot_locations.json', 'w') as fp:
    json.dump(selected_nodes_dic, fp)