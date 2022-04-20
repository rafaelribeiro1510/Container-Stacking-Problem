import json
from typing import Optional, Union
from ContainerMatrix import ContainerMatrix
from ortools.sat.python import cp_model

# Sum of each box is equal to that containers lifetime, at each given t
def c1(model : cp_model.CpModel, matrix : ContainerMatrix):
    for t in range(matrix.t):
        for c in range(matrix.c):
            model.Add(sum(matrix.get_range(t, c, None, None), 0) == matrix.lifetime[t][c])

# No two containers can exist in the same place, at each given t
def c2(model : cp_model.CpModel, matrix : ContainerMatrix):
    for t in range(matrix.t):
        for s in range(matrix.s):
            for h in range(matrix.h):
                model.Add(sum(matrix.get_range(t, None, s, h), 0) <= 1)

# Sum of top part of stack must be lower or equal to sum of bottom part. Forbids floating containers
def c3(model : cp_model.CpModel, matrix : ContainerMatrix):
    for t in range(matrix.t):
        for s in range(matrix.s):
            for h in range(matrix.h):
                if h == 0:
                    continue
                model.Add(sum(matrix.get_range(t, None, s, h), 0) <= sum(matrix.get_range(t, None, s, h - 1), 0))

# For each time t, only one action can be chosen
def c4(model : cp_model.CpModel, matrix : ContainerMatrix):
    for trio in zip(matrix.emplace, matrix.idle, matrix.remove):
        model.Add(sum(trio) == 1)

# Restricts whether 'in' or 'out' can exist in the decision grids, based on the action that was chosen, at each time t
def c5(model : cp_model.CpModel, matrix : ContainerMatrix):
    for t in range(matrix.t - 1):
        model.Add(sum(matrix.decision_get_range(t, "in",  None, None), 0) == matrix.emplace[t])
        model.Add(sum(matrix.decision_get_range(t, "out", None, None), 0) == 1 - matrix.idle[t])

# For each time t, there cannot be both 'in' and 'out' on the same position
def c6(model : cp_model.CpModel, matrix : ContainerMatrix):
    ins = matrix.decision_get_range(None, "in",  None, None)
    outs = matrix.decision_get_range(None, "out",  None, None)

    for i, o in zip(ins, outs):
        b = model.NewBoolVar('b')

        model.Add(i == 1).OnlyEnforceIf(b)
        model.Add(i == 0).OnlyEnforceIf(b.Not())
        # This is a bit scuffed: b is True -> i == 1, b is False -> i == 0
        # Therefore, b <=> (i == 1)

        model.Add(o == 0).OnlyEnforceIf(b)

# An 'out' must be put on a place where a container exists, on a given time t
def c7(model : cp_model.CpModel, matrix : ContainerMatrix):
    for t in range(matrix.t - 1):
        for s in range(matrix.s):
            for h in range(matrix.h):
                b = model.NewBoolVar('b')
                out = matrix.decision_get(t, "out", s, h)
                model.Add(out == 1).OnlyEnforceIf(b)
                model.Add(out == 0).OnlyEnforceIf(b.Not())

                model.Add(sum(matrix.get_range(t, None, s, h)) == out).OnlyEnforceIf(b)

# At the start, all containers are 'alive'
def c8(model : cp_model.CpModel, matrix : ContainerMatrix):
    model.Add(sum(matrix.lifetime[0]) == matrix.c)

# When a 'remove' action is chosen, the number of 'live' containers is reduced by one (1)
def c9(model : cp_model.CpModel, matrix : ContainerMatrix):
    for t in range(matrix.t - 1):
        model.Add(sum(matrix.lifetime[t]) == sum(matrix.lifetime[t + 1]) + matrix.remove[t])

# When a container stops existing, it won't reappear
def c10(model : cp_model.CpModel, matrix : ContainerMatrix):
    for t in range(matrix.t - 1):
        for c in range(matrix.c):
            model.Add(matrix.lifetime[t][c] >= matrix.lifetime[t + 1][c])

# If the action 'idle' is chosen, everything stays the same
def c11(model : cp_model.CpModel, matrix : ContainerMatrix):
    for t in range(matrix.t - 1):
        for c in range(matrix.c):
            for s in range(matrix.s):
                for h in range(matrix.h):
                    b = model.NewBoolVar('b')
                    model.Add(matrix.idle[t] == 1).OnlyEnforceIf(b)
                    model.Add(matrix.idle[t] == 0).OnlyEnforceIf(b.Not())

                    model.Add(matrix.get(t, c, s, h) == matrix.get(t + 1, c, s, h)).OnlyEnforceIf(b)

# If the action 'remove' is chosen, everything stays the same, except for the place marked with an 'out' in the decision grid
def c12(model : cp_model.CpModel, matrix : ContainerMatrix):
    for t in range(matrix.t - 1):
        for c in range(matrix.c):
            for s in range(matrix.s):
                for h in range(matrix.h):
                    b = model.NewBoolVar('b')
                    model.Add(matrix.remove[t] == 1).OnlyEnforceIf(b)
                    model.Add(matrix.remove[t] == 0).OnlyEnforceIf(b.Not())

                    b1 = model.NewBoolVar('b1')
                    model.Add(matrix.decision_get(t, "out", s, h) == 1).OnlyEnforceIf(b1)
                    model.Add(matrix.decision_get(t, "out", s, h) == 0).OnlyEnforceIf(b1.Not())

                    model.Add(matrix.get(t, c, s, h) == matrix.get(t + 1, c, s, h)).OnlyEnforceIf(b, b1.Not())

# If the action 'emplace' is chosen, if a place has no container and there is no 'in' for that place, it will remain with no containers
def c13(model : cp_model.CpModel, matrix : ContainerMatrix):
    for t in range(matrix.t - 1):
        for c in range(matrix.c):
            for s in range(matrix.s):
                for h in range(matrix.h):
                    b = model.NewBoolVar('b')
                    model.Add(matrix.emplace[t] == 1).OnlyEnforceIf(b)
                    model.Add(matrix.emplace[t] == 0).OnlyEnforceIf(b.Not())

                    b1 = model.NewBoolVar('b1')
                    model.Add(matrix.get(t, c, s, h) == 1).OnlyEnforceIf(b1)
                    model.Add(matrix.get(t, c, s, h) == 0).OnlyEnforceIf(b1.Not())

                    b2 = model.NewBoolVar('b2')
                    model.Add(matrix.decision_get(t, "in", s, h) == 1).OnlyEnforceIf(b2)
                    model.Add(matrix.decision_get(t, "in", s, h) == 0).OnlyEnforceIf(b2.Not())

                    model.Add(matrix.get(t + 1, c, s, h) == 0).OnlyEnforceIf(b, b1.Not(), b2.Not())

# If the action 'emplace' is chosen and there is an 'in' in a place, then in the next timestamp, there will be a container in that place
def c14(model : cp_model.CpModel, matrix : ContainerMatrix):
    for t in range(matrix.t - 1):
        for s in range(matrix.s):
            for h in range(matrix.h):
                b = model.NewBoolVar('b')
                model.Add(matrix.emplace[t] == 1).OnlyEnforceIf(b)
                model.Add(matrix.emplace[t] == 0).OnlyEnforceIf(b.Not())

                b1 = model.NewBoolVar('b1')
                model.Add(matrix.decision_get(t, "in", s, h) == 1).OnlyEnforceIf(b1)
                model.Add(matrix.decision_get(t, "in", s, h) == 0).OnlyEnforceIf(b1.Not())

                model.Add(sum(matrix.get_range(t, None, s, h))     == 0).OnlyEnforceIf(b, b1)
                model.Add(sum(matrix.get_range(t + 1, None, s, h)) == 1).OnlyEnforceIf(b, b1)

# If the action 'emplace' is chosen and there is an 'out' in a place, then in the next timestamp, there will be no container in that place
def c15(model : cp_model.CpModel, matrix : ContainerMatrix):
    for t in range(matrix.t - 1):
        for s in range(matrix.s):
            for h in range(matrix.h):
                b = model.NewBoolVar('b')
                model.Add(matrix.emplace[t] == 1).OnlyEnforceIf(b)
                model.Add(matrix.emplace[t] == 0).OnlyEnforceIf(b.Not())

                b1 = model.NewBoolVar('b1')
                model.Add(matrix.decision_get(t, "out", s, h) == 1).OnlyEnforceIf(b1)
                model.Add(matrix.decision_get(t, "out", s, h) == 0).OnlyEnforceIf(b1.Not())

                model.Add(sum(matrix.get_range(t, None, s, h))     == 1).OnlyEnforceIf(b, b1)
                model.Add(sum(matrix.get_range(t + 1, None, s, h)) == 0).OnlyEnforceIf(b, b1)

def load_from_json(json_path : str):
    with open(json_path) as f:
        data = json.load(f)

    time, length, height = data["dimensions"]
    n_containers = len(data["containers"])

    index_lookup = {label : index for index, label in enumerate(i[0] for i in data["containers"])}
    labels = [i[0] for i in data["containers"]]

    model = cp_model.CpModel()
    matrix = ContainerMatrix(model, time, n_containers, length, height)

    constraints = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15]
    for constraint in constraints: 
        constraint(model, matrix)
    
    # Setting the initial container positions
    for container, (label, stack, height) in enumerate(data["containers"]):
        model.Add(matrix.get(0, container, stack, height) == 1)
    
    model.Maximize(sum(matrix.idle)) # By maximizing the number of idle actions, we minimize emplaces and removes

    for label in labels:
        should_exist = 0 if label in data["remove"] else 1 # If 0, the container should be removed
        model.Add(matrix.lifetime[-1][index_lookup[label]] == should_exist)
    
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        matrix.print_solution(solver, labels=labels)

def main(time : int, container : int, length : int, height : int):
    model = cp_model.CpModel()

    matrix = ContainerMatrix(model, time, container, length, height)

    constraints = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15]
    for constraint in constraints: 
        constraint(model, matrix)

    model.Add(sum(matrix.emplace) == 6) # This is just here for debug

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        matrix.print_solution(solver)

if __name__ == '__main__':
    # main(10, 4, 4, 3)
    load_from_json("input.json")