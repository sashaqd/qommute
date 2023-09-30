from pyqubo import Binary
from pyqubo import Array
from pprint import pprint
import neal

import json

from qiskit.utils import algorithm_globals
from qiskit.algorithms.minimum_eigensolvers import QAOA, NumPyMinimumEigensolver
from qiskit.algorithms.optimizers import COBYLA
from qiskit.primitives import Sampler
from qiskit_optimization.algorithms import (
    MinimumEigenOptimizer,
    RecursiveMinimumEigenOptimizer,
    SolutionSample,
    OptimizationResultStatus,
)
from qiskit_optimization import QuadraticProgram
from qiskit.visualization import plot_histogram
from typing import List, Tuple
import numpy as np

from qiskit_optimization.translators import from_docplex_mp
from docplex.mp.model import Model

class QUBO:
    def __init__(self, graph, rw_graph, bw_centrality):
        self.graph = rw_graph
        self.bw_centrality = bw_centrality
        self.node_dict = graph.node_dict
        self.index_dict = graph.index_dict
        self.H = self.get_hamiltonian(self.node_dict, self.index_dict, self.bw_centrality, self.graph)
        self.model = self.H.compile()

        self.qubo, self.offset = self.model.to_qubo()
        self.bqm = self.model.to_bqm()

        self.nodes = len(self.node_dict)

    def get_hamiltonian(self, node_dict: dict, index_dict: dict, bw_centrality, graph):
        """
        Takes a dictionary of nodes and a dictionary of indices as input and returns the Hamiltonian of the problem

        Parameters
        ----------
        node_dict : dict
            A dictionary of nodes with the name of the city as key and a tuple of latitude and longitude as value
        index_dict : dict
            A dictionary of indices with the name of the city as key and a tuple of latitude and longitude as value

        Returns
        -------
        H : pyqubo.core.express.Add
            The Hamiltonian of the problem
        """
        nodes = len(node_dict)
        #create an array of binary variables in our Hamiltonian.
        #x[i] = 1 if a sensor is placed at that node, 0 otherwise
        x = Array.create('x', shape=(nodes), vartype='BINARY')

        #####calculate H_1#####
        H_1 = 0
        weight_max = None

        for edge in graph.edge_list():

            # here weight (cost) is betweenness centrality of nodes in the edge
            weight = bw_centrality[edge[0]] + bw_centrality[edge[1]]

            if weight_max is None or weight > weight_max:
                weight_max = weight

        H_1 += (1-x[edge[0]])*(1-x[edge[1]])*weight

        H_1 *= 1/weight_max

        #####calculate H_2#####
        H_2 = 0

        for i in range(len(index_dict)):
        # here cost c = Cf(i) + Dg(i)
            cost = graph[i]["c"]
            H_2 += x[i]*cost

        #####calculate H_3#####

        #number of sensors we want to place
        stations = 4
        H_3 = (sum(x)-stations)**2

        #####Get Hamiltonian function#####
        A,B,C = 100,100,100 #random coef for now
        H = A*H_1 + B*H_2 + C*H_3

        return H

    def get_neal_solution(self):
        """
        Gets the solution to the problem using neal
        """
        sa = neal.SimulatedAnnealingSampler()
        sampleset = sa.sample(self.bqm, num_reads=10)

        decoded_samples = self.model.decode_sampleset(sampleset)

        best_sample = min(decoded_samples, key=lambda x: x.energy)

        return best_sample.sample

    def save_solution_to_json(self, coordinates, solution, file_path):
        """
        Saves the solution to a json file

        Parameters
        ----------
        solution : dict
            A dictionary of solutions with the name of the city as key and a tuple of latitude and longitude as value
        file_path : str
            The path to the json file
        """
        # extract the node information from the best sample
        selected_nodes = []
        index = 0
        for key, value in solution.items():
            if value == 1:
                selected_nodes.append(index)
            index += 1

        # extracting the name and coordinates of the selected nodes into a dictionary then to a json file
        selected_nodes_dic = {"depots": []}
        for i in selected_nodes:
            for key, value in self.index_dict.items():
                if value == i:
                    selected_nodes_dic["depots"].append({"lat": coordinates[key][0], "lon": coordinates[key][1]})

        with open(file_path, 'w') as fp:
            json.dump(selected_nodes_dic, fp)
    
    def create_problem(self) -> QuadraticProgram:
        result = []
        mdl = Model()

        x = [mdl.binary_var("x%s" % i) for i in range(self.nodes)]

        res = []
        for (var1, var2), coef in self.qubo.items():

            #gettinggthe index from the var strings
            v1 = int(var1[2:len(var1)-1])
            v2 = int(var2[2:len(var2)-1])

            res.append(x[v1] * x[v2] * coef)

        objective = mdl.sum(res)
        mdl.minimize(objective)
        cost = (mdl.sum(x))
        #mdl.add_constraint(cost == total)

        qp = from_docplex_mp(mdl)

        return qp
    
    def run_qaoa(self, qubo: QuadraticProgram):
        algorithm_globals.random_seed = 10598
        qaoa_mes = QAOA(sampler=Sampler(), optimizer=COBYLA(), initial_point=[0.0, 0.0])
        result = MinimumEigenOptimizer(qaoa_mes).solve(qubo)

        return result
    
    def run_exact(self, qubo: QuadraticProgram):
        algorithm_globals.random_seed = 10598
        exact_mes = NumPyMinimumEigensolver()
        result = MinimumEigenOptimizer(exact_mes).solve(qubo)

        return result