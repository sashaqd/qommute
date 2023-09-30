import rustworkx
import matplotlib.pyplot as plt
from rustworkx.visualization import mpl_draw

from getter_functions import get_no_of_people_at_station, get_distance_from_farthest_metro, get_delay_from_nearest_station, normalize

class Graph:
    def __init__(self, coordinates, selected_coordinates, station_distances, f_list, g_list, h_list) -> None:
        self.coordinates = coordinates
        self.selected_coordinates = selected_coordinates
        self.station_distances = station_distances
        self.f_list = f_list
        self.g_list = g_list
        self.h_list = h_list
        self.node_dict, self.edge_dict, self.index_dict = self.create_nodes_edges(self.selected_coordinates, self.station_distances)
        self.graph = self.make_graph(self.node_dict, self.edge_dict, self.index_dict)


    def create_nodes_edges(self, selected_coordinates:dict, station_distances:dict):
        """
        Takes a dictionary of coordinates and a dictionary of distances between stations as input and returns a dictionary of nodes and edges

        Parameters
        ----------
        selected_coordinates : dict
            A dictionary of coordinates with the name of the city as key and a tuple of latitude and longitude as value
        station_distances : dict
            A dictionary of distances between stations with the name of the city as key and a tuple of latitude and longitude as value

        Returns
        -------
        node_dict : dict
            A dictionary of nodes with the name of the city as key and a tuple of latitude and longitude as value
        edge_dict : dict
            A dictionary of edges with the name of the city as key and a tuple of latitude and longitude as value
        index_dict : dict
            A dictionary of indices with the name of the city as key and a tuple of latitude and longitude as value
        """
        node_dict = {}
        edge_dict = {}
        index_dict = {}

        for (key, _) in selected_coordinates.items():
            if (key in self.f_list.keys()) and (key in self.g_list.keys()) and (key in self.h_list.keys()):
                node_dict[key] = { 'name':key, 'f': self.f_list[key], 'g': self.g_list[key], 'h': self.h_list[key] }

        #constants
        C = 5
        D = 3
        E = 0.3

        temp = {node: {"name": attrs["name"], "c": C*attrs["f"] + D*attrs["g"] + E*attrs["h"]}
                    for node, attrs in node_dict.items()}
        node_dict = temp

        index = 0
        for node in node_dict:
            index_dict[node] = index
            index += 1
        
        for item in station_distances.items():
            if (item[0][0] in node_dict) and (item[0][1] in node_dict) and item[1] <= 25:
                edge_dict[item[0]] = {'cost': item[1]}
        
        return node_dict, edge_dict, index_dict

    def make_graph(self, node_dict: dict, edge_dict: dict, index_dict: dict):
        """
        Takes a dictionary of nodes and a dictionary of edges as input and returns a graph

        Parameters
        ----------
        node_dict : dict
            A dictionary of nodes with the name of the city as key and a tuple of latitude and longitude as value
        edge_dict : dict
            A dictionary of edges with the name of the city as key and a tuple of latitude and longitude as value
        index_dict : dict
            A dictionary of indices with the name of the city as key and a tuple of latitude and longitude as value

        Returns
        -------
        graph : rustworkx.PyGraph
            A graph
        """

        graph = rustworkx.PyGraph()

        for node in node_dict.items():
            graph.add_node(node[1])

        for edge in edge_dict.items():
            graph.add_edge( index_dict[edge[0][0]] , index_dict[edge[0][1]] , edge[1]["cost"])

        return graph