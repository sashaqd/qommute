import json

from bus_routing import QuantumOptimizer, BusRoutingInstance, visualize_solution

# get the location of the depots from a JSON file
def get_depots(file_name, no_of_depots=2):
    with open(file_name) as json_file:
        data = json.load(json_file)
        depots = data["depots"]
        return depots[:no_of_depots]

depot_locations = get_depots("./bus_depot_locations.json", no_of_depots=3) # depot locations refer to where the buses visit to pick up passengers

# defining the parameters of the problem
n = len(depot_locations) # number of depots
K = 2 # number of buses

init = BusRoutingInstance(n)
xcoor, ycoor, instance = init.generate_instance(depot_locations)

# Instantiate the quantum optimizer class with parameters:
optim = QuantumOptimizer(instance, n, K)

# Get the binary representation of the problem
Q, g, c, binary_cost = optim.binary_representation()

# Construct the problem
qp = optim.construct_problem(Q, g, c, n)

# Solve the problem
x, cost = optim.solve_problem(qp)

# Visualize the solution
visualize_solution(xcoor, ycoor, x, cost, n, K, "Quantum Solution")

# Print the solution
print("Quantum Solution: ", x)
print("Quantum Solution Cost: ", cost)

# save the visualization into a file
import matplotlib.pyplot as plt
plt.savefig('./bus_routing.png')