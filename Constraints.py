from ContainerMatrix import ContainerMatrix
from Model import Model

# Sum of each box is equal to that containers lifetime, at each given t
def c1(model : Model, matrix : ContainerMatrix):
    for t in range(matrix.t):
        for c in range(matrix.c):
            model.Add(sum(matrix.get_range(t, c, None, None), 0) == matrix.lifetime[t][c])

# No two containers can exist in the same place, at each given t
def c2(model : Model, matrix : ContainerMatrix):
    for t in range(matrix.t):
        for s in range(matrix.s):
            for h in range(matrix.h):
                model.Add(sum(matrix.get_range(t, None, s, h), 0) <= 1)

# Sum of top part of stack must be lower or equal to sum of bottom part. Forbids floating containers
def c3(model : Model, matrix : ContainerMatrix):
    for t in range(matrix.t):
        for s in range(matrix.s):
            for h in range(matrix.h):
                if h == 0:
                    continue
                model.Add(sum(matrix.get_range(t, None, s, h), 0) <= sum(matrix.get_range(t, None, s, h - 1), 0))

# For each time t, only one action can be chosen
def c4(model : Model, matrix : ContainerMatrix):
    for quartet in zip(matrix.emplace, matrix.idle, matrix.remove, matrix.insert):
        model.Add(sum(quartet) == 1)

# Restricts whether 'in' or 'out' can exist in the decision grids, based on the action that was chosen, at each time t
def c5(model : Model, matrix : ContainerMatrix):
    for t in range(matrix.t - 1):
        model.Add(sum(matrix.decision_get_range(t, "in",  None, None), 0) == matrix.emplace[t] + matrix.insert[t])
        model.Add(sum(matrix.decision_get_range(t, "out", None, None), 0) == matrix.emplace[t] + matrix.remove[t])

# For each time t, there cannot be both 'in' and 'out' on the same position
def c6(model : Model, matrix : ContainerMatrix):
    ins = matrix.decision_get_range(None, "in",  None, None)
    outs = matrix.decision_get_range(None, "out",  None, None)

    for i, o in zip(ins, outs):
        b = model.NewBoolVar('b')

        model.AddIf(i == 1, b)
        model.AddIf(i == 0, model.Not(b))
        # This is a bit scuffed: b is True -> i == 1, b is False -> i == 0
        # Therefore, b <=> (i == 1)

        model.AddIf(o == 0, b)

# An 'out' must be put on a place where a container exists, on a given time t
def c7(model : Model, matrix : ContainerMatrix):
    for t in range(matrix.t - 1):
        for s in range(matrix.s):
            for h in range(matrix.h):
                b = model.NewBoolVar('b')
                out = matrix.decision_get(t, "out", s, h)
                model.AddIf(out == 1, b)
                model.AddIf(out == 0, model.Not(b))

                model.AddIf(sum(matrix.get_range(t, None, s, h)) == out, b)

# When a 'remove'  action is chosen, the number of 'live' containers is reduced   by one (1)
# When an 'insert' action is chosen, the number of 'live' containers is increased by one (1)
def c9(model : Model, matrix : ContainerMatrix):
    for t in range(matrix.t - 1):
        model.Add(sum(matrix.lifetime[t]) == sum(matrix.lifetime[t + 1]) + matrix.remove[t] - matrix.insert[t])

# When a container stops existing, it won't reappear
def c10(model : Model, matrix : ContainerMatrix):
    for t in range(matrix.t - 1):
        for c in range(matrix.c):
            not_insert = model.NewBoolVar('b')
            model.AddIf(matrix.insert[t] == 0, not_insert)
            model.AddIf(matrix.insert[t] == 1, model.Not(not_insert))
            model.AddIf(matrix.lifetime[t][c] >= matrix.lifetime[t + 1][c], not_insert)

# If the action 'idle' is chosen, everything stays the same
def c11(model : Model, matrix : ContainerMatrix):
    for t in range(matrix.t - 1):
        for c in range(matrix.c):
            for s in range(matrix.s):
                for h in range(matrix.h):
                    b = model.NewBoolVar('b')
                    model.AddIf(matrix.idle[t] == 1, b)
                    model.AddIf(matrix.idle[t] == 0, model.Not(b))

                    model.AddIf(matrix.get(t, c, s, h) == matrix.get(t + 1, c, s, h), b)

# If the action 'remove' is chosen, everything stays the same, except for the place marked with an 'out' in the decision grid
def c12(model : Model, matrix : ContainerMatrix):
    for t in range(matrix.t - 1):
        for c in range(matrix.c):
            for s in range(matrix.s):
                for h in range(matrix.h):
                    b = model.NewBoolVar('b')
                    model.AddIf(matrix.remove[t] == 1, b)
                    model.AddIf(matrix.remove[t] == 0, model.Not(b))

                    b1 = model.NewBoolVar('b1')
                    model.AddIf(matrix.decision_get(t, "out", s, h) == 1, b1)
                    model.AddIf(matrix.decision_get(t, "out", s, h) == 0, model.Not(b1))

                    model.AddIf(matrix.get(t, c, s, h) == matrix.get(t + 1, c, s, h), b, model.Not(b1))

# If the action 'emplace' is chosen, if a place has no container and there is no 'in' for that place, it will remain with no containers
def c13(model : Model, matrix : ContainerMatrix):
    for t in range(matrix.t - 1):
        for c in range(matrix.c):
            for s in range(matrix.s):
                for h in range(matrix.h):
                    b = model.NewBoolVar('b')
                    model.AddIf(matrix.emplace[t] == 1, b)
                    model.AddIf(matrix.emplace[t] == 0, model.Not(b))

                    b1 = model.NewBoolVar('b1')
                    model.AddIf(matrix.get(t, c, s, h) == 1, b1)
                    model.AddIf(matrix.get(t, c, s, h) == 0, model.Not(b1))

                    b2 = model.NewBoolVar('b2')
                    model.AddIf(matrix.decision_get(t, "in", s, h) == 1, b2)
                    model.AddIf(matrix.decision_get(t, "in", s, h) == 0, model.Not(b2))

                    model.AddIf(matrix.get(t + 1, c, s, h) == 0, b, model.Not(b1), model.Not(b2))

# If the action 'emplace' is chosen and there is an 'in' in a place, then in the next timestamp, there will be a container in that place
def c14(model : Model, matrix : ContainerMatrix):
    for t in range(matrix.t - 1):
        for s in range(matrix.s):
            for h in range(matrix.h):
                b = model.NewBoolVar('b')
                model.AddIf(matrix.emplace[t] == 1, b)
                model.AddIf(matrix.emplace[t] == 0, model.Not(b))

                b1 = model.NewBoolVar('b1')
                model.AddIf(matrix.decision_get(t, "in", s, h) == 1, b1)
                model.AddIf(matrix.decision_get(t, "in", s, h) == 0, model.Not(b1))

                model.AddIf(sum(matrix.get_range(t, None, s, h))     == 0, b, b1)
                model.AddIf(sum(matrix.get_range(t + 1, None, s, h)) == 1, b, b1)

# If the action 'emplace' is chosen and there is an 'out' in a place, then in the next timestamp, there will be no container in that place
def c15(model : Model, matrix : ContainerMatrix):
    for t in range(matrix.t - 1):
        for s in range(matrix.s):
            for h in range(matrix.h):
                b = model.NewBoolVar('b')
                model.AddIf(matrix.emplace[t] == 1, b)
                model.AddIf(matrix.emplace[t] == 0, model.Not(b))

                b1 = model.NewBoolVar('b1')
                model.AddIf(matrix.decision_get(t, "out", s, h) == 1, b1)
                model.AddIf(matrix.decision_get(t, "out", s, h) == 0, model.Not(b1))

                model.AddIf(sum(matrix.get_range(t, None, s, h))     == 1, b, b1)
                model.AddIf(sum(matrix.get_range(t + 1, None, s, h)) == 0, b, b1)


# If the action 'insert' is chosen, every container that previously existed stays in the same place
def c16(model : Model, matrix : ContainerMatrix):
    for t in range(matrix.t - 1):
        for c in range(matrix.c):
            for s in range(matrix.s):
                for h in range(matrix.h):
                    insert = model.NewBoolVar('b')
                    model.AddIf(matrix.insert[t] == 1, insert)
                    model.AddIf(matrix.insert[t] == 0, model.Not(insert))

                    b1 = model.NewBoolVar('b1')
                    model.AddIf(matrix.decision_get(t, "in", s, h) == 1, b1)
                    model.AddIf(matrix.decision_get(t, "in", s, h) == 0, model.Not(b1))

                    model.AddIf(matrix.get(t, c, s, h) == matrix.get(t + 1, c, s, h), insert, model.Not(b1))