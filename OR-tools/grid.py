from ortools.sat.python import cp_model

def main(length : int, height : int):
    model = cp_model.CpModel()

    vars_ = []

    # Generating all the variables
    for h in range(height):
        new_line = []
        for l in range(length):
            new_line.append(
                model.NewIntVar(0, 1, f"h{h}l{l}")
            )

        vars_.append(new_line)
    
    # Setting a constraint
    sum_ = 0 
    for line in vars_[::-1]:
        for v in line:
            sum_ += v
    
    model.Add(sum_ == 1)
    
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for line in vars_[::-1]:
            for v in line:
                print(f"{solver.Value(v)} ", end="")
            print()

if __name__ == '__main__':
    main(4, 3)