from getter_functions import get_no_of_people_at_station, get_distance_from_nearest_site, get_delay_from_nearest_station, normalize

import rustworkx
import matplotlib.pyplot as plt
from rustworkx.visualization import mpl_draw

def make_node_edge(selected_coordinates, stations_dic):
    """
    Make a list of nodes and edges from the selected coordinates and stations dictionary
    
    Parameters
    ----------
    selected_coordinates : dict
        Dictionary of selected coordinates
    stations_dic : dict
        Dictionary of stations and their distances

    Returns
    -------
    node_dic : dict
        Dictionary of nodes
    index_dic : dict
        Dictionary of node indices
    edge_dic : dict
        Dictionary of edges
    """
    #node dictionary
    node_dic = {}
    f_list = get_no_of_people_at_station(selected_coordinates)
    g_list = get_distance_from_nearest_site(selected_coordinates)
    h_list = get_delay_from_nearest_station(selected_coordinates)

    f_list = normalize(f_list)
    g_list = normalize(g_list)
    h_list = normalize(h_list)

    # print(f_list)

    for (key, _) in selected_coordinates.items():
        # print(key)
        if (key in f_list) and (key in g_list):
            node_dic[key] = { 'name':key , 'f': f_list[key] , 'g': g_list[key], 'h': h_list[key]}

    C = 5
    D = 3
    E = 0.3

    temp = {node: {"name": attrs["name"], "c": C*attrs["f"] + D*attrs["g"] + E*attrs["h"]}
                    for node, attrs in node_dic.items()}
    node_dic = temp

    #node index dictionary
    index_dic = {}

    index = 0
    for node in node_dic:
        index_dic[node] = index
    index+=1

    # #edge dictionary
    # edge_dic = {}

    # # edges only between nodes w 30 min distance
    # for item in stations_dic.items():
    #   dur = item[1]
    #   if dur <= 30:
    #     edge_dic[item[0]] = {'cost': dur}

    # will add edges for all the nodes considered
    edge_dic = {}
    for item in stations_dic.items():
        if (item[0][0] in node_dic) and (item[0][1] in node_dic) and item[1] <= 25:
            edge_dic[item[0]] = {'cost': item[1]}

    return node_dic, index_dic, edge_dic

def make_graph(node_dic, index_dic, edge_dic):
    """
    Make a graph from the node and edge dictionaries
    
    Parameters
    ----------
    node_dic : dict
        Dictionary of nodes
    index_dic : dict
        Dictionary of node indices
    edge_dic : dict
        Dictionary of edges

    Returns
    -------
    graph : rustworkx
        Graph of nodes and edges
    """
    graph = rustworkx.Graph()

    for node in node_dic:
        graph.add_node(index_dic[node], **node_dic[node])

    for edge in edge_dic:
        graph.add_edge(index_dic[edge[0]], index_dic[edge[1]], **edge_dic[edge])

    return graph