import argparse
import json
from inspect import getmembers, isfunction

from ContainerMatrix import ContainerMatrix
from Model import Model
import Constraints as Constraints


def load_from_json(json_path : str, solver_name : str):
    with open(json_path) as f:
        data = json.load(f)
        print("Input file loaded: '" + json_path + "'")

    time, length, height = data["dimensions"]
    n_containers = len(data["containers"])

    index_lookup = {label : index for index, label in enumerate(i[0] for i in data["containers"])}
    labels = [i[0] for i in data["containers"]]

    model = Model(solver_name)
    matrix = ContainerMatrix(model, time, n_containers, length, height)

    constraints = getmembers(Constraints, isfunction)
    for _, constraint in constraints: 
        # print(_)
        constraint(model, matrix)
    
    # Setting the initial container positions
    for container, (label, stack, height) in enumerate(data["containers"]):
        model.Add(matrix.get(0, container, stack, height) == 1)
    
    model.Maximize(sum(matrix.idle)) # By maximizing the number of idle actions, we minimize emplaces and removes

    for label in labels:
        should_exist = 0 if label in data["remove"] else 1 # If 0, the container should be removed
        model.Add(matrix.lifetime[-1][index_lookup[label]] == should_exist)
    
    status = model.Solve()

    if status == model.OPTIMAL or status == model.FEASIBLE:
        matrix.print_solution(model, labels=labels)

if __name__ == '__main__':
    my_parser = argparse.ArgumentParser(description='Run the solver for the Container Stacking Problem')

    my_parser.add_argument('-solver',
        metavar='--solver-package',
        type=str,
        required=True,
        choices=['ortools', 'cplex'],
        help="choice of solver to solve input problem. Currently supports 'ortools' and 'cplex'")

    my_parser.add_argument('-path',
        metavar='--input-path',
        type=str,
        default='inputs/input.json',
        help="the path to the file with the input problem (.json). By default is 'inputs/input.json'")
    args = my_parser.parse_args()

    load_from_json(args.path, args.solver)