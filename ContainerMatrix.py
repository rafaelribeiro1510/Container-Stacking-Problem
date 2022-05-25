import string
from typing import Tuple, List, Union
import pygame

from Model import Model

COLORS = [
    (230, 25, 75), 
    (60, 180, 75), 
    (255, 225, 25), 
    (0, 130, 200), 
    (245, 130, 48), 
    (145, 30, 180), 
    (70, 240, 240),
    (240, 50, 230), 
    (210, 245, 60), 
    (250, 190, 212), 
    (0, 128, 128),
    (220, 190, 255), 
    (170, 110, 40), 
    (255, 250, 200), 
    (128, 0, 0), 
    (170, 255, 195), 
    (128, 128, 0), 
    (255, 215, 180), 
    (0, 0, 128), 
    (128, 128, 128), 
    (255, 255, 255), 
    (0, 0, 0),
]

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
        self.insert = []
        self.decision_variables = {}

        for time in range(t - 1):
            self.idle.append(model.NewIntVar(0, 1, f"d{time}idle"))
            self.remove.append(model.NewIntVar(0, 1, f"d{time}remove"))
            self.emplace.append(model.NewIntVar(0, 1, f"d{time}emplace"))
            self.insert.append(model.NewIntVar(0, 1, f"d{time}insert"))
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
        print("Decisions: ", end="")
        decisions = []
        for i in range(len(self.emplace)):
            if   model.Value(self.emplace[i]) == 1:
                decisions.append("Em")
            elif model.Value(self.idle[i])    == 1:
                decisions.append("Id")
            elif model.Value(self.remove[i])  == 1:
                decisions.append("Re")
            elif model.Value(self.insert[i])  == 1:
                decisions.append("In")
        print("[" + ", ".join(decisions) + "]")

        if detail:
            self.print_decisions(model)
        decision_spacer = (((self.s + 1) * 2) * (self.t - 1) - 1)
        print("=" * decision_spacer)
        self.print_condensed_decisions(model)
        print("=" * decision_spacer)
    
    def visualize(self, model : Model, labels : Union[List[str], str] = None):
        if labels == None:
            labels = list(string.ascii_uppercase)[:self.c]
        pygame.init()
        win = pygame.display.set_mode((self.s * 36 + 300, self.h * 36 + 100))
        pygame.display.set_caption("Container animation")

        font = pygame.font.SysFont(None, 50)

        state = 0
        state_already_changed = False

        run = True
        while run:
            pygame.time.delay(10)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                if not state_already_changed:
                    state -= 1
                    state_already_changed = True
            elif keys[pygame.K_RIGHT]:
                if not state_already_changed:
                    state += 1
                    state_already_changed = True
            else:
                state_already_changed = False
                    
            state = max(0, min(state, len(self.idle)))


            win.fill((255, 255, 255))

            img = font.render(f"t={state}", True, (0, 0, 0))
            win.blit(img, (self.s * 36 + 220, 20))

            next_instruction = None
            if state < self.t - 1:
                if   model.Value(self.idle[state])    == 1:
                    next_instruction = "Idle"
                elif model.Value(self.emplace[state]) == 1:
                    next_instruction = "Emplace"
                elif model.Value(self.remove[state])  == 1:
                    next_instruction = "Remove"
                elif model.Value(self.insert[state])  == 1:
                    next_instruction = "Insert"
            else:
                next_instruction = "Done"

            img = pygame.font.SysFont(None, 25).render(f"Next instruction: {next_instruction}", True, (0, 0, 0))
            win.blit(img, (20, 20))

            X = 36 * self.s / 2 + 100
            Y = 36 * self.h + 50

            for height in reversed(range(self.h)):
                for stack in range(self.s):
                    v_range = self.get_range(state, None, stack, height, no_dimensions=False)
                    for v in v_range:
                        if model.Value(v[4]) != 0:
                            background_color = COLORS[v[1] % len(COLORS)]
                            foreground_color = (0, 0, 0) if sum(background_color) / 3 >= 256 / 2 else (255, 255, 255)

                            name = labels[v[1]]
                            img = font.render(name, True, foreground_color)
                            pygame.draw.rect(win, background_color, (X + stack * 36 + 1, Y - height * 36 + 1, 35, 35))
                            win.blit(img, (X + stack * 36 + 2, Y - height * 36 + 4))
                            break
                    else:
                        pygame.draw.rect(win, (240, 240, 240), (X + stack * 36 + 1, Y - height * 36 + 1, 35, 35))

            pygame.display.update()

        pygame.quit()
