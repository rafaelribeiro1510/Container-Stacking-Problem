# PLR Project

## Concept
Dock management system that handles loading of desired containers to each ship.
### Formal definition
There is a list of stacks of containers that represent the dockyard and a list of stacks of containers that represent the ship. Only some of these containers must be loaded on the ship. The goal is to load all desired containers using the smallest possible amount of container moving operations, all while respecting the maximum stack size, for both the dockyard and ship areas. Initial research suggests that this is a classic optimzation problem named *Container Stacking Problem*.

### Stretch goals
- The dock has a budget of actions that it can execute before a ship arrives (would be used to optimize the dock layout for this next shipment)
- Multiple ships
- A heavier container must not be placed above a lighter one, at any time.
- Container stacks have a maximum height.
- Ships could have containers onboard, that must be unloaded
- 3D considerations on ships (??)
- Fully describe crane travel costs (moving up, sideways & down)

## Implementation
### Technologies
- Google OR
- IBM CPLEX

### Data structures
- Dock & Ship layout
    - List of stacks
        - Containers
            - Ship destination
            - Weight

## Relevant papers
[The parallel stack loading problem to minimize blockages](https://www.sciencedirect.com/science/article/pii/S0377221715008759)

- deterministic information on both the arrival sequence and the priority weights, which at least “can be very useful as a benchmark”

> **Papers mentioned**
> 
>[Caserta, Voss, Sniedovich, 2011b](https://www.sciencedirect.com/science/article/pii/S0377221715008759#bib0011) : Unloading problem (also denoted as the block relocation problem), where a sequence of items is to be retrieved from the stacks, such that the number of relocation moves for removing blocking boxes is minimized.

[Two-stage search algorithm for the inbound container unloading and stacking problem](https://www.sciencedirect.com/science/article/pii/S0307904X19305074)

[An effective heuristic algorithm to minimise stack shuffles in selecting steel slabs from the slab yard for heating and rolling](https://link.springer.com/article/10.1057/palgrave.jors.2601143) (good reference for understanding stacks in OR)

[Heuristic search for the stacking problem](https://www.dcc.fc.up.pt/~jpp/publications/PDF/stacking-itor-preview.pdf)

[Ant Colony Optimization for Solving the Container Stacking Problem: Case of Le Havre (France) Seaport Terminal](https://www.researchgate.net/profile/Jalel-Euchi/publication/316267058_Ant_Colony_Optimization_for_Solving_the_Container_Stacking_Problem/links/5979b3764585154d23b44323/Ant-Colony-Optimization-for-Solving-the-Container-Stacking-Problem.pdf)

[Interactive ILP procedures for stacking optimization for the 3D palletization problem](https://www.tandfonline.com/doi/pdf/10.1080/002075497195326) (more complex than we need)

## Problem Formulation

### Simplifications
- On all versions of the problem, the solution is a sequence of moving actions.
- When a container is moved from the yard to the ship, it is essentially removed from the problem, since this is tracked by the output corresponding action.
    - Unlike mentioned papers' works, all notion of position inside the ship is disregarded. No ship stacks or ship indexes are tracked.
    
### Decision Variables
$M_{tcsh}$ - Matrix of binary values that represent the state of the dockyard, at any given time $t$.
    - Time axis $t$ 
    - Containers axis $c$
    - Stack number axis $s$
    - Stack index (height) axis $h$
    
$D_{t}$ - List of actions $A$, of same dimension $t$ as the state, that represents the sequence of actions taken to reach the target state.

$A_{c(s,h)(s',h')}$ - Action that represents moving container $c$ from stack $s$ at index $h$, to stack $s'$ at index $h'$. The pair $(s', h')$ can be null, which signifies that the container was moved to the ship.

### Constraints
> Constraints (2) and (3) ensure that the assignment of boxes to storage positions is well defined, that is, **each container receives one storage position and each position at most one container**.

**Idea for floating container restriction:**
1. Vector of [0, 1] to verify container is at height N. 
2. For every index of N, verify that product of values of all lower indexes is equal to the value at N.

**Professor sugestion:**
- For each pair i, j of consequent indexes of a stack, where $i<j$, $x_i <= x_j$.

## Attack plan
1. Very small problem with 2 stacks, one is empty, the other has 3 containers. The container that must be moved to the target is at the bottom. The other two must stay on yard. [Search problem]
2. Variable number N stacks of fixed height h, with fixed number c of containers. [Search problem]
3. Same as before, but with empty incoming ships to receive containers. Down time before each ship arrives can be used to rearrange yard. [Minimization problem]
