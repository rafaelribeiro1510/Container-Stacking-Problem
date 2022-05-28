import argparse
import json
from inspect import getmembers, isfunction

from ContainerMatrix import ContainerMatrix
from Model import Model
import Constraints as Constraints

def enforce_container_lifetime_restrictions(model : Model, matrix : ContainerMatrix, labels, index_lookup, initial_container_positions, shipments, time):
    for container in labels:
        # This is the life cycle of the containers
        dead       = [None, None]
        in_        = [None, None]
        alive      = [None, None]
        out        = [None, None]
        dead_again = [None, None]

        dead = [0, 0]

        for shipment in shipments:
            if alive == [None, None] and container in (c[0] for c in initial_container_positions):
                dead = [0, 0]
                in_  = [0, 0]
                alive = [0, shipment["duration"]]
                continue

            if in_ == [None, None]:
                if "in" not in shipment:
                    dead[1] += shipment["duration"]
                elif container not in shipment["in"]:
                    dead[1] += shipment["duration"]
                elif container in shipment["in"]:
                    in_ = [dead[1], dead[1] + shipment["duration"]]
                else:
                    raise Exception("Unreachable code")
                
            elif alive == [None, None]:
                alive = [in_[1], in_[1] + shipment["duration"]]

            elif out == [None, None]:
                if "out" not in shipment:
                    alive[1] += shipment["duration"]
                elif container not in shipment["out"]:
                    alive[1] += shipment["duration"]
                elif container in shipment["out"]:
                    out = [alive[1], alive[1] + shipment["duration"]]
                    dead_again = [alive[1] + shipment["duration"], time]
                    break
                else:
                    raise Exception("Unreachable code")
        
        if out == [None, None] and dead_again == [None, None]:
            out = [time, time]
            dead_again = [time, time]
        
        # print(f"{dead=} {in_=} {alive=} {out=} {dead_again=}")
        # input()

        for t in range(time):
            if dead[0] <= t < dead[1] or dead_again[0] <= t < dead_again[1]:
                model.Add(matrix.lifetime[t][index_lookup[container]] == 0)
            elif alive[0] <= t < alive[1]:
                model.Add(matrix.lifetime[t][index_lookup[container]] == 1)
        
    final_shipment = shipments[-1]
    if "in" in final_shipment and "out" in final_shipment:
        for c in final_shipment["in"]:
            model.Add(matrix.lifetime[-1][index_lookup[c]] == 1)
        for c in final_shipment["out"]:
            model.Add(matrix.lifetime[-1][index_lookup[c]] == 0)

def load_from_json(json_path : str, solver_name : str):
    with open(json_path) as f:
        data = json.load(f)
        print("Input file loaded: '" + json_path + "'")

    length, height = data["dimensions"]
    shipments = data["shipments"]
    time = sum(shipment["duration"] for shipment in shipments)

    initial_container_positions = data["containers"]

    containers = [i[0] for i in initial_container_positions]
    for shipment in shipments:
        if "in" in shipment:
            containers += shipment["in"]

    index_lookup = {label : index for index, label in enumerate(containers)}
    labels = containers

    model = Model(solver_name)
    print("Generating matrix")
    matrix = ContainerMatrix(model, time, len(containers), length, height)

    print("Implementing matrix constraints")
    constraints = getmembers(Constraints, isfunction)
    for _, constraint in constraints: 
        # print(_)
        constraint(model, matrix)
    
    print("Setting initial container positions")
    for container, (label, stack, height) in enumerate(initial_container_positions):
        model.Add(matrix.get(0, container, stack, height) == 1)
    
    print("Setting initial container lifetime")
    for i, container in enumerate(containers):
        if container in [i[0] for i in initial_container_positions]:
            model.Add(matrix.lifetime[0][i] == 1)
        else:
            model.Add(matrix.lifetime[0][i] == 0)

    print("Enforcing container lifetime restrictions")
    enforce_container_lifetime_restrictions(model, matrix, labels, index_lookup, initial_container_positions, shipments, time)
    
    model.Maximize(sum(matrix.idle)) # By maximizing the number of idle actions, we minimize emplaces and removes and inserts
    
    print("solving")
    status = model.Solve()

    if status == model.OPTIMAL or status == model.FEASIBLE:
        # matrix.print_solution(model, labels=labels)
        print("Visualizing")
        matrix.visualize(model, labels=labels)

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