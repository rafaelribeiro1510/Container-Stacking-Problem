from ortools.sat.python import cp_model
from typing import Tuple, List, Union


class ContainerMatrix:
    def __init__(self, model : cp_model.CpModel, t : int, c : int, s : int, h : int) -> None:
        self.model = model
        self.t = t
        self.c = c
        self.s = s
        self.h = h
        self.variables = {}

        for time in range(t):
            for container in range(c):
                for stack in range(s):
                    for height in range(h):
                        identifier = f"t{time}c{container}s{stack}h{height}"
                        self.variables[(time, container, stack, height)] = model.NewIntVar(0, 1, identifier)
    
    def get(self, t : int, c : int, s : int, h : int) -> cp_model.CpModel:
        self.validate_query_dimensions(t, c, s, h)

        return self.variables[(t, c, s, h)]
    
    def get_range(self, t : Union[int, None], c : Union[int, None], s : Union[int, None], h : Union[int, None], no_dimensions = True) -> Union[List[Tuple[int, int, int, int, cp_model.CpModel]], List[cp_model.CpModel]]:
        self.validate_query_dimensions(t, c, s, h)
        
        result = []

        for key, variable in self.variables.items():
            skip = False
            for dimension, index in zip([t, c, s, h], [0, 1, 2, 3]):
                if dimension != None and dimension != key[index]:
                    skip = True
            if skip:
                continue

            result.append(
                (*key, variable)
            )
        
        sorted_result = list(sorted(result))

        if no_dimensions:
            return [e[4] for e in sorted_result]
        else:
            return sorted_result
    
    def validate_query_dimensions(self, t : Union[int, None], c : Union[int, None], s : Union[int, None], h : Union[int, None]):
        for query, dimension in zip([t, c, s, h], [self.t, self.c, self.s, self.h]):
            if query != None:
                assert query < dimension
    
    def print_solution(self, solver : cp_model.CpSolver):
        print("""
            -----time---->
           |     
           |     
        container
           |     
           V             """)
        for container in range(self.c):
            print()
            for height in reversed(range(self.h)):
                for time in range(self.t):
                    for stack in range(self.s):
                        v = self.get(time, container, stack, height)
                        print(f"{solver.Value(v)} ", end="")
                    print("| ", end="")
                print(chr(65 + container))

        print("=" * (((self.s + 1) * 2) * self.t - 1))
        for height in reversed(range(self.h)):
            for time in range(self.t):
                for stack in range(self.s):
                    v_range = self.get_range(time, None, stack, height, no_dimensions=False)
                    for v in v_range:
                        if solver.Value(v[4]) != 0:
                            print(chr(65 + v[1]) + " ", end="")
                            break
                    else:
                        print(". ", end="")
                print("| ", end="")
            print()