import random
import rustworkx
import matplotlib.pyplot as plt
from rustworkx.visualization import mpl_draw
from getter_functions import get_train_station_location, calculate_distance_from_api, get_station_distance, min_max_normalize, get_number_riders, clean, get_distance_from_nearest_site
from graph_utils import make_node_edge, make_graph, visualize
from qubo import QUBOPlacement

class bikeStationPlanner:
    def __init__(self):
        # Step 1: Get the bike station locations
        self.coordinates = get_train_station_location("bike_placement/data/DOITT_SUBWAY_STATION_01_13SEPT2010.csv")

        # f
        self.station_rider_sums = get_number_riders("bike_placement/data/Annual Total-Table 1.csv")

        # clean data
        self.coordinates, self.station_rider_sums = clean(self.coordinates, self.station_rider_sums)

        # Step 2: Get the distance between the bike stations
        self.stations_dic = get_station_distance(self.coordinates, "bike_placement/data/stations.csv")

        # g
        self.min_station_dist = get_distance_from_nearest_site(self.stations_dic)

        # Make a list of nodes and edges from the selected coordinates and stations dictionary
        self.node_dic, self.index_dic, self.edge_dic = make_node_edge(self.station_rider_sums, self.min_station_dist, self.stations_dic)

        # Step 3: Make a graph and calculate the betweenness centrality
        self.graph, self.bw_centrality = make_graph(self.node_dic, self.index_dic, self.edge_dic)

    def create_qubo(self):
        # Step 5: Get the QUBO coefficients
        self.qubo = QUBOPlacement(self.graph, self.bw_centrality, self.node_dic, self.index_dic)

    def solve_qubo(self):
        # Step 6: Create the QUBO problem
        qubo_form = self.qubo.create_problem()

        # Step 7: Get the best sample
        best_sample = self.qubo.get_best_sample()
        print("Printing best sample:")
        print(best_sample)

        # # Step 8: Run a simulation with QAOA and also the exact solver
        # qaoa_result = qubo.run_qaoa()
        # exact_result = qubo.run_exact()

        # # # Step 9: Print the results
        # print("Printing QAOA result:")
        # print(qaoa_result.pretty_print())
        # print("Printing exact result:")
        # print(exact_result.pretty_print())
        return best_sample

    def save_selected_nodes(self,best_sample):
        # Step 10: Save the results for the routing problem
        # Extract the node information from the best sample
        selected_nodes = []
        index = 0
        for key, value in best_sample.items():
            if value == 1:
                selected_nodes.append(index)
            index += 1

        # Extracting the name and coordinates of the selected nodes into a dictionary then to a json file
        selected_nodes_dic = {"depots": []}
        for i in selected_nodes:
            for key, value in self.index_dic.items():
                if value == i:
                    selected_nodes_dic["depots"].append({"lat": self.coordinates[key][0], "lon": self.coordinates[key][1]})

        import json
        with open('bike_placement/citi_bike_locations.json', 'w') as fp:
            json.dump(selected_nodes_dic, fp)

# DEMO

if __name__ == "__main__":
    bike_station_planner = bikeStationPlanner()
    bike_station_planner.create_qubo()
    best_sample = bike_station_planner.solve_qubo()
    bike_station_planner.save_selected_nodes(best_sample)
