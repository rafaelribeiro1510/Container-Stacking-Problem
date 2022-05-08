import sys
import json
from inspect import getmembers, isfunction

from ContainerMatrix import ContainerMatrix
from Model import Model
import Constraints as Constraints


def load_from_json(json_path : str):
    with open(json_path) as f:
        data = json.load(f)

    time, length, height = data["dimensions"]
    n_containers = len(data["containers"])

    index_lookup = {label : index for index, label in enumerate(i[0] for i in data["containers"])}
    labels = [i[0] for i in data["containers"]]

    model = Model(ortools=True)
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
    if len(sys.argv) == 2:
        load_from_json(sys.argv[1])
    elif len(sys.argv) == 1:
        load_from_json("inputs/input.json") # Default json