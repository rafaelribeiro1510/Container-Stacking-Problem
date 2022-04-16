from ContainerMatrix import ContainerMatrix
from ortools.sat.python import cp_model

def c1(model : cp_model.CpModel, matrix : ContainerMatrix):
    for t in range(matrix.t):
        for c in range(matrix.c):
            model.Add(sum(matrix.get_range(t, c, None, None), 0) == 1)

def c2(model : cp_model.CpModel, matrix : ContainerMatrix):
    for t in range(matrix.t):
        for s in range(matrix.s):
            for h in range(matrix.h):
                model.Add(sum(matrix.get_range(t, None, s, h), 0) <= 1)

def c3(model : cp_model.CpModel, matrix : ContainerMatrix):
    for t in range(matrix.t):
        for s in range(matrix.s):
            for h in range(matrix.h):
                if h == 0:
                    continue
                model.Add(sum(matrix.get_range(t, None, s, h), 0) <= sum(matrix.get_range(t, None, s, h - 1), 0))

def c4(model : cp_model.CpModel, matrix : ContainerMatrix):
    for trio in zip(matrix.emplace, matrix.idle, matrix.remove):
        model.Add(sum(trio) == 1)

def c5(model : cp_model.CpModel, matrix : ContainerMatrix):
    for t in range(matrix.t - 1):
        model.Add(sum(matrix.decision_get_range(t, "in",  None, None), 0) == matrix.emplace[t])
        model.Add(sum(matrix.decision_get_range(t, "out", None, None), 0) == 1 - matrix.idle[t])
        
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

def main(time : int, container : int, length : int, height : int):
    model = cp_model.CpModel()

    matrix = ContainerMatrix(model, time, container, length, height)

    c1(model, matrix)
    c2(model, matrix)
    c3(model, matrix)
    c4(model, matrix)
    c5(model, matrix)
    c6(model, matrix)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:

        matrix.print_solution(solver)

if __name__ == '__main__':
    main(4, 4, 4, 3)