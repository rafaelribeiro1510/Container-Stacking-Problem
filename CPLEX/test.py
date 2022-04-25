from docplex.mp.model import Model
m = Model(name='single variable')
x = m.continuous_var(name="x", lb=0)
c1 = m.add_constraint(x >= 2, ctname="const1")
m.set_objective("min", 3*x)
m.print_information()
m.solve()
m.print_solution()