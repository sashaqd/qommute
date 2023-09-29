import random

import rustworkx
import matplotlib.pyplot as plt
from rustworkx.visualization import mpl_draw

from getter_functions import get_train_station_location, calculate_distance_from_api, get_station_distance, min_max_normalize, get_number_riders, clean, get_distance_from_nearest_site
from graph_utils import make_node_edge, make_graph, visualize
from qubo import QUBOPlacement

# Step 1: Get the bus station locations
coordinates = get_train_station_location("data/DOITT_SUBWAY_STATION_01_13SEPT2010.csv")

# f
station_rider_sums = get_number_riders("data/Annual Total-Table 1.csv")

#clean data
station_rider_sums = clean(coordinates, station_rider_sums)

# Step 2: Get the distance between the bus stations
stations_dic = get_station_distance("data/stations.csv")

# g
min_station_dist = get_distance_from_nearest_site(stations_dic)


# Step 3: Make a graph and calculate the betweenness centrality
node_dic, index_dic, edge_dic = make_node_edge(station_rider_sums, min_station_dist,stations_dic )
graph, bw_centrality = make_graph(node_dic, index_dic, edge_dic)


# # Create a larger figure with a specified size (adjust the values as needed)
# fig = plt.figure(figsize=(50, 50))

# # Create a subplot within the larger figure
# subax1 = plt.subplot(121)

# # Now, you can draw your graph with_labels=True on the larger subplot
# mpl_draw(graph, with_labels=True, ax=subax1)

# # Show the plot
# plt.show()

# Step 5: Get the QUBO coefficients
qubo = QUBOPlacement(graph, bw_centrality, node_dic, index_dic)

qubo_form = qubo.create_problem()

# Step 6: Get the best sample
best_sample = qubo.get_best_sample()
print("Printing best sample:")
print(best_sample)

# Step 7: Run a simulation with QAOA and also the exact solver
qaoa_result = qubo.run_qaoa()
exact_result = qubo.run_exact()

# Step 8: Print the results
print("Printing QAOA result:")
print(qaoa_result.pretty_print())
print("Printing exact result:")
print(exact_result.pretty_print())

# Step 9: Save the results for the routing problem
# extract the node information from the best sample

# selected_nodes = []
# index = 0
# for key, value in best_sample.sample.items():
#   if value == 1:
#     selected_nodes.append(index)
#   index += 1

# # extracting the name and coordinates of the selected nodes into a dictionary then to a json file
# selected_nodes_dic = {"depots": []}
# for i in selected_nodes:
#    for key, value in index_dic.items():
#       if value == i:
#         selected_nodes_dic["depots"].append({"lat": coordinates[key][0], "lon": coordinates[key][1]})


# import json
# with open('../routing/bus_depot_locations.json', 'w') as fp:
#     json.dump(selected_nodes_dic, fp)