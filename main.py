import timeit
import argparse
import json
from inspect import getmembers, isfunction

from numpy import number

from ContainerMatrix import ContainerMatrix
from Model import Model
import Constraints as Constraints

def positive_int(x):
    i = int(x)
    if i < 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive integer value" % x)
    return i
def positive_float(x):
    f = float(x)
    if f < 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive float value" % x)
    return f

def load_from_json(args : object, logs : bool = True):
    with open(args.path) as f:
        data = json.load(f)
        
        if logs:
            print("Input file loaded: '" + args.path + "'")

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
    
    solution = model.Solve(args.time)

    if logs:
        if solution['status'] == model.OPTIMAL or solution['status'] == model.FEASIBLE:
            print('Solution time (s)', solution['time'])
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

    my_parser.add_argument('-benchmark',
        metavar='--benchmark-runs',
        nargs='?',
        type=positive_int,
        default=0,
        help="number of runs for benchmarking time (recommended: 5)")
    
    my_parser.add_argument('-time',
        metavar='--max-time',
        nargs='?',
        type=positive_float,
        default=0,
        help="time limit (in seconds) to return solution. Either returns sub-optimal one, or none")
    args = my_parser.parse_args()

    if args.benchmark == 0:
        load_from_json(args)

    else:
        t = timeit.Timer(lambda: load_from_json(args, logs=False))
        print("Solver [", args.solver, "]")
        print("Number runs [", args.benchmark, "]")
        print("Time avg(s): ", t.timeit(args.benchmark)/args.benchmark)