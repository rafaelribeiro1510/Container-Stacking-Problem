from ortools.sat.python.cp_model import CpModel, CpSolver, OPTIMAL, FEASIBLE
from docplex.cp.model import CpoModel
from docplex.cp.solution import SOLVE_STATUS_OPTIMAL, SOLVE_STATUS_FEASIBLE

class Model:
    def __init__(self, solver_name : str) -> None:
        if solver_name == 'ortools':
            self.ortools = CpModel()
            self.cplex = False
        elif solver_name == 'cplex':
            self.cplex = CpoModel()
            self.ortools = False
        else:
            raise Exception("Solver not supported")

    # Model methods
    def Not(self, b):
        if self.ortools:
            return b.Not()
        elif self.cplex:
            return 1 - b

    def NewIntVar(self, min, max, identifier):
        if self.ortools:
            return self.ortools.NewIntVar(min, max, identifier)
        elif self.cplex:
            return self.cplex.integer_var(min, max, identifier)

    def NewBoolVar(self, i):
        if self.ortools:
            return self.ortools.NewBoolVar(i)
        elif self.cplex:
            return self.cplex.binary_var(i)
        
    def Add(self, expr):
        if self.ortools:
            return self.ortools.Add(expr)
        elif self.cplex:
            return self.cplex.add(expr)

    def AddIf(self, expr, *b):
        if self.ortools:
            return self.ortools.Add(expr).OnlyEnforceIf(b)
        elif self.cplex:
            
            return self.cplex.add(self.cplex.if_then(sum(b) == len(b), expr))

    # Solver methods
    def Maximize(self, expr):
        if self.ortools:
            return self.ortools.Maximize(expr)
        elif self.cplex:
            return self.cplex.add(self.cplex.maximize(expr))

    def Value(self, expr):
        if self.ortools:
            return self.solver.Value(expr)
        elif self.cplex:
            return self.solver.get_value(expr)

    def Solve(self, max_time=0):
        if self.ortools:
            self.OPTIMAL = OPTIMAL
            self.FEASIBLE = FEASIBLE
            self.solver = CpSolver()
            
            if max_time > 0:
                self.solver.parameters.max_time_in_seconds = max_time
            
            status = self.solver.Solve(self.ortools)
            return {
                "status": status,
                "time": self.solver.WallTime(),
                "objective": self.solver.ObjectiveValue()
            }
        elif self.cplex:
            self.OPTIMAL = SOLVE_STATUS_OPTIMAL
            self.FEASIBLE = SOLVE_STATUS_FEASIBLE
            
            if max_time > 0:
                self.cplex.parameters.timelimit = max_time

            self.solver = self.cplex.solve(execfile='/opt/ibm/ILOG/CPLEX_Studio201/cpoptimizer/bin/x86-64_linux/cpoptimizer', log_output=False)
            return {
                "status": self.solver.get_solve_status(),
                "time": self.solver.get_solve_time(),
                "objective": self.solver.objective_value
            }
