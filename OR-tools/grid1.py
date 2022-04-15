from ContainerMatrix import ContainerMatrix
from ortools.sat.python import cp_model

def c1(model, matrix):
    for t in range(matrix.t):
        for c in range(matrix.c):
            model.Add(sum(matrix.get_range(t, c, None, None), 0) == 1)

def c2(model, matrix):
    for t in range(matrix.t):
        for s in range(matrix.s):
            for h in range(matrix.h):
                model.Add(sum(matrix.get_range(t, None, s, h), 0) <= 1)

def main(time : int, container : int, length : int, height : int):
    model = cp_model.CpModel()

    matrix = ContainerMatrix(model, time, container, length, height)

    c1(model, matrix)
    c2(model, matrix)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:

        matrix.print_solution(solver)

if __name__ == '__main__':
    main(4, 4, 4, 3)