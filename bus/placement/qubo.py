from pyqubo import Binary
from pyqubo import Array
from pprint import pprint
import neal

from qiskit.utils import algorithm_globals
from qiskit.algorithms.minimum_eigensolvers import QAOA, NumPyMinimumEigensolver
from qiskit.algorithms.optimizers import COBYLA
from qiskit.primitives import Sampler
from qiskit_optimization.algorithms import (
    MinimumEigenOptimizer,
)
from qiskit_optimization import QuadraticProgram
from qiskit.visualization import plot_histogram
from typing import List, Tuple
import numpy as np

from qiskit_optimization.translators import from_docplex_mp
from docplex.mp.model import Model


class QUBOPlacement:
    def __init__(self, graph, bw_centrality):
        self.graph = graph
        self.bw_centrality = bw_centrality
    
    def get_qubo(self):
        #create a dictionary of nodes and their index
        node_dic = {}
        index_dic = {}
        index = 0
        for node in self.graph.nodes():
            node_dic[node] = index
            index_dic[index] = node
        index += 1
    
        #number of nodes in the graph
        nodes = len(node_dic)
    
        #create an array of binary variables in our Hamiltonian.
        #x[i] = 1 if a sensor is placed at that node, 0 otherwise
        x = Array.create('x', shape=(nodes), vartype='BINARY')
    
        #####calculate H_1#####
        H_1 = 0
        weight_max = None
    
        for edge in self.graph.edge_list():
            # here weight (cost) is betweenness centrality of nodes in the edge
            weight = self.bw_centrality[edge[0]] + self.bw_centrality[edge[1]]
        
            if weight_max is None or weight > weight_max:
                weight_max = weight
    
            H_1 += (1-x[edge[0]])*(1-x[edge[1]])*weight
    
        H_1 *= 1/weight_max
    
        #####calculate H_2#####
        H_2 = 0
    
        for i in range(len(index_dic)):
            # here cost c = Cf(i) + Dg(i)
            cost = self.graph[i]["c"]
            H_2 += x[i]*cost
    
        #####calculate H_3#####
    
        #number of sensors we want to place
        stations = 4
        H_3 = (sum(x)-stations)**2
    
        #####Get Hamiltonian function#####
        A,B,C = 100,100,100 #random coef for now
        H = A*H_1 + B*H_2 + C*H_3
    
        #Compile the Hamiltonian to get a model
        model = H.compile()
    
        #get and print QUBO coefficients
        qubo, offset = model.to_qubo()
        #print("Printing QUBO coefficients:")
        #pprint(qubo)
    
        return qubo, offset, model, index_dic
    
    def get_best_sample(self, model, index_dic):
        #Solve BinaryQuadraticModel(BQM) by using Sampler class
        bqm = model.to_bqm()
    
        #get the solutions of QUBO as SampleSet
        sa = neal.SimulatedAnnealingSampler()
        sampleset = sa.sample(bqm, num_reads=1000)
    
        #interpret the sampleset object
        decoded_samples = model.decode_sampleset(sampleset)
        #print the decoded_samples
        #print("Printing the decoded sample:")
        #pprint(decoded_samples)
    
        best_sample = min(decoded_samples, key=lambda x: x.energy)
    
        #print the best sample
        #print("Printing the best sample:")
        #pprint(best_sample.sample)
    
        return best_sample.sample

    def create_problem(self, qubo_dict , nodes) -> QuadraticProgram:
        result = []
        mdl = Model()

        x = [mdl.binary_var("x%s" % i) for i in range(nodes)]

        res = []
        for (var1, var2), coef in qubo_dict.items():

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
    
    def run_qaoa(self, qubo_dict, node_dic):
        qubo = self.create_problem(qubo_dict[0], len(node_dic))
        print(qubo.prettyprint())

        op, offset = qubo.to_ising()
        print("offset: {}".format(offset))
        print("operator:")
        print(op)

        algorithm_globals.random_seed = 10598
        qaoa_mes = QAOA(sampler=Sampler(), optimizer=COBYLA(), initial_point=[0.0, 0.0])
        exact_mes = NumPyMinimumEigensolver()

        qaoa = MinimumEigenOptimizer(qaoa_mes)
    
        qaoa_result = qaoa.solve(qubo)
        # print(qaoa_result.prettyprint())

        return qaoa_result

    def run_exact(self, qubo_dict, node_dic):
        qubo = self.create_problem(qubo_dict[0], len(node_dic))
        print(qubo.prettyprint())

        op, offset = qubo.to_ising()
        print("offset: {}".format(offset))
        print("operator:")
        print(op)

        algorithm_globals.random_seed = 10598
        qaoa_mes = QAOA(sampler=Sampler(), optimizer=COBYLA(), initial_point=[0.0, 0.0])
        exact_mes = NumPyMinimumEigensolver()

        exact = MinimumEigenOptimizer(exact_mes)
    
        exact_result = exact.solve(qubo)
        # print(exact_result.prettyprint())

        return exact_result