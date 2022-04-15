from ContainerMatrix import ContainerMatrix
from ortools.sat.python import cp_model

def main(time : int, container : int, length : int, height : int):
    model = cp_model.CpModel()

    matrix = ContainerMatrix(model, time, container, length, height)

    for t in range(time):
        for c in range(container):
            model.Add(sum(matrix.get_range(t, c, None, None), 0) == 1)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:

        matrix.print_solution(solver)

if __name__ == '__main__':
    main(4, 4, 4, 3)