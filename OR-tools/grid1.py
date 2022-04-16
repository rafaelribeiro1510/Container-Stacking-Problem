from ContainerMatrix import ContainerMatrix
from ortools.sat.python import cp_model

def c1(model : cp_model.CpModel, matrix : ContainerMatrix):
    for t in range(matrix.t):
        for c in range(matrix.c):
            model.Add(sum(matrix.get_range(t, c, None, None), 0) == matrix.lifetime[t][c])

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

def c7(model : cp_model.CpModel, matrix : ContainerMatrix):
    for t in range(matrix.t - 1):
        for s in range(matrix.s):
            for h in range(matrix.h):
                b = model.NewBoolVar('b')
                out = matrix.decision_get(t, "out", s, h)
                model.Add(out == 1).OnlyEnforceIf(b)
                model.Add(out == 0).OnlyEnforceIf(b.Not())

                model.Add(sum(matrix.get_range(t, None, s, h)) == out).OnlyEnforceIf(b)

def c8(model : cp_model.CpModel, matrix : ContainerMatrix):
    model.Add(sum(matrix.lifetime[0]) == matrix.c)

def c9(model : cp_model.CpModel, matrix : ContainerMatrix):
    for t in range(matrix.t - 1):
        model.Add(sum(matrix.lifetime[t]) == sum(matrix.lifetime[t + 1]) + matrix.remove[t])

def c10(model : cp_model.CpModel, matrix : ContainerMatrix):
    for t in range(matrix.t - 1):
        for c in range(matrix.c):
            model.Add(matrix.lifetime[t][c] >= matrix.lifetime[t + 1][c])

def c11(model : cp_model.CpModel, matrix : ContainerMatrix):
    for t in range(matrix.t - 1):
        for c in range(matrix.c):
            for s in range(matrix.s):
                for h in range(matrix.h):
                    b = model.NewBoolVar('b')
                    model.Add(matrix.idle[t] == 1).OnlyEnforceIf(b)
                    model.Add(matrix.idle[t] == 0).OnlyEnforceIf(b.Not())

                    model.Add(matrix.get(t, c, s, h) == matrix.get(t + 1, c, s, h)).OnlyEnforceIf(b)

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


def main(time : int, container : int, length : int, height : int):
    model = cp_model.CpModel()

    matrix = ContainerMatrix(model, time, container, length, height)

    c1(model, matrix)
    c2(model, matrix)
    c3(model, matrix)
    c4(model, matrix)
    c5(model, matrix)
    c6(model, matrix)
    c7(model, matrix)
    c8(model, matrix)
    c9(model, matrix)
    c10(model, matrix)
    c11(model, matrix)
    c12(model, matrix)
    c13(model, matrix)
    c14(model, matrix)
    c15(model, matrix)

    model.Add(sum(matrix.emplace) == 6) # This is just here for debug

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:

        matrix.print_solution(solver)

if __name__ == '__main__':
    main(10, 4, 4, 3)