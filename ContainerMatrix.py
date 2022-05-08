import string
from typing import Tuple, List, Union
from pprint import pprint

from Model import Model

class ContainerMatrix:
    def __init__(self, model : Model, t : int, c : int, s : int, h : int) -> None:
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

        self.lifetime = []

        for time in range(t):
            temp = []
            for container in range(c):
                temp.append(
                    model.NewIntVar(0, 1, "l")
                )
            self.lifetime.append(temp)
        
        self.idle = []
        self.remove = []
        self.emplace = []
        self.decision_variables = {}

        for time in range(t - 1):
            self.idle.append(model.NewIntVar(0, 1, f"d{time}i"))
            self.remove.append(model.NewIntVar(0, 1, f"d{time}r"))
            self.emplace.append(model.NewIntVar(0, 1, f"d{time}e"))
            for stack in range(s):
                for height in range(h):
                    identifier = f"d{time}s{stack}h{height}"
                    self.decision_variables[(time, "in",  stack, height)] = model.NewIntVar(0, 1, identifier + "in")
                    self.decision_variables[(time, "out", stack, height)] = model.NewIntVar(0, 1, identifier + "out")            
    
    def get(self, t : int, c : int, s : int, h : int) -> Model:
        self.validate_query_dimensions(t, c, s, h)

        return self.variables[(t, c, s, h)]
    
    def decision_get(self, t : int, m : int, s : int, h : int) -> Model:
        self.validate_query_dimensions(t, None, s, h)
        assert m in ("in", "out")

        return self.decision_variables[(t, m, s, h)]
    
    def get_range(self, t : Union[int, None], c : Union[int, None], s : Union[int, None], h : Union[int, None], no_dimensions = True) -> Union[List[Tuple[int, int, int, int, Model]], List[Model]]:
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
    
    def decision_get_range(self, t : Union[int, None], m : Union[int, None], s : Union[int, None], h : Union[int, None], no_dimensions = True) -> Union[List[Tuple[int, int, int, int, Model]], List[Model]]:
        self.validate_query_dimensions(t, None, s, h)
        assert m in (None, "in", "out")

        result = []

        for key, variable in self.decision_variables.items():
            skip = False
            for dimension, index in zip([t, m, s, h], [0, 1, 2, 3]):
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
    
    def print_guidance(self):
        print("""
            -----time---->
           |     
           |     
        container
           |     
           V             """)
    
    def print_binary_grid(self, model : Model):
        for container in range(self.c):
            print()
            for height in reversed(range(self.h)):
                for time in range(self.t):
                    for stack in range(self.s):
                        v = self.get(time, container, stack, height)
                        print(f"{model.Value(v)} ", end="")
                    print("| ", end="")
                print(chr(65 + container))
    
    def print_condensed_grid(self, model : Model, labels : List[str]):
        for height in reversed(range(self.h)):
            for time in range(self.t):
                for stack in range(self.s):
                    v_range = self.get_range(time, None, stack, height, no_dimensions=False)
                    for v in v_range:
                        if model.Value(v[4]) != 0:
                            print(labels[v[1]] + " ", end="")
                            break
                    else:
                        print(". ", end="")
                print("| ", end="")
            print()

    def print_decisions(self, model : Model):
        for movement in ("in", "out"):
            print()
            for height in reversed(range(self.h)):
                for time in range(self.t - 1):
                    for stack in range(self.s):
                        v = self.decision_get(time, movement, stack, height)
                        print(f"{model.Value(v)} ", end="")
                    print("| ", end="")
                print(" " + movement)
    
    def print_condensed_decisions(self, model : Model):
        for height in reversed(range(self.h)):
            for time in range(self.t - 1):
                for stack in range(self.s):
                    v_range = self.decision_get_range(time, None, stack, height, no_dimensions=False)
                    for v in v_range:
                        if model.Value(v[4]) != 0:
                            print("O " if v[1] == "out" else "I ", end="")
                            break
                    else:
                        print(". ", end="")
                print("| ", end="")
            print()

    def print_lifetimes(self, model : Model, labels : List[str]):
        print("LIFETIMES:")
        t = zip(*self.lifetime)

        for i, v in enumerate(t):
            print(f"{labels[i]}: {[model.Value(e) for e in v]}")

    def print_solution(self, model : Model, detail : bool = False, labels : Union[List[str], str] = None):
        # self.print_guidance()
        if detail:
            self.print_binary_grid(model)
        
        if labels == None:
            labels = list(string.ascii_uppercase)[:self.c]

        spacer = (((self.s + 1) * 2) * self.t - 1)
        print("=" * spacer)
        self.print_condensed_grid(model, labels)
        print("=" * spacer)
        
        self.print_lifetimes(model, labels)

        # pprint(self.decision_variables)
        print("DECISION VARIABLES")
        print(f"Emplace: {[model.Value(e) for e in self.emplace]}")
        print(f"Idle:    {[model.Value(e) for e in self.idle]}")
        print(f"Remove:  {[model.Value(e) for e in self.remove]}")

        if detail:
            self.print_decisions(model)
        decision_spacer = (((self.s + 1) * 2) * (self.t - 1) - 1)
        print("=" * decision_spacer)
        self.print_condensed_decisions(model)
        print("=" * decision_spacer)
