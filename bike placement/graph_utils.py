
import rustworkx
import matplotlib.pyplot as plt
from rustworkx.visualization import mpl_draw
import matplotlib.pyplot as plt

def make_node_edge(station_rider_sums, min_station_dist,stations_dic ):
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

    # creating and cleaning a node dictionary
    node_dictionary = {}
    for item in stations_dic.items():
        node_dictionary[item[0][0]] = 1
        node_dictionary[item[0][1]] = 1

    node_dic = {}

    for item in node_dictionary.items():
        node_dic[item[0]] = { 'name':item[0] ,
                            'f': station_rider_sums[item[0]] ,
                            'g': min_station_dist[item[0]] }

    C = 0.01
    D = 0.01

    temp = {node: {"name": attrs["name"], "c": C*attrs["f"] + D*attrs["g"]}
                    for node, attrs in node_dic.items()}
    node_dic = temp

    #node index dictionary
    index_dic = {}

    index = 0
    for node in node_dic:
        index_dic[node] = index
        index+=1

    #edge dictionary
    edge_dic = {}

    # edges only between nodes w 30 min distance
    for item in stations_dic.items():
        dur = item[1]
        if dur <= 40:
            edge_dic[item[0]] = {'cost': dur}

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
    graph = rustworkx.PyGraph()

    for node in node_dic.items():
        graph.add_node(node[1])

    for edge in edge_dic.items():
        graph.add_edge( index_dic[edge[0][0]] , index_dic[edge[0][1]] , edge[1]["cost"])

    # Calculate the betweenness centrality for each node
    bw_centrality = rustworkx.betweenness_centrality(graph)

    return graph, bw_centrality

def visualize(bw_centrality, graph):
    # Generate a color list
    colors = []
    for node in graph.node_indices():
        colors.append(bw_centrality[node])

    # Create a larger figure with a specified size
    plt.figure(figsize=(200, 200))

    # Generate a visualization with a colorbar
    plt.rcParams['figure.figsize'] = [15, 10]
    ax = plt.gca()
    sm = plt.cm.ScalarMappable(norm=plt.Normalize(
        vmin=min(bw_centrality.values()),
        vmax=max(bw_centrality.values())
    ))
    plt.colorbar(sm, ax=ax)
    plt.title("Betweenness Centrality : ")

    # Draw the graph with enlarged size
    mpl_draw(graph, node_color=colors, ax=ax)

    # Show the plot
    plt.show()