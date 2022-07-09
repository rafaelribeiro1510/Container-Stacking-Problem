# Container Stacking Problem

- **Project name:** Container Stacking Problem
- **Short description:** Formulation of and solution to a problem of ship container loading and unloading operation
- **Environment:** Unix
- **Tools:** Python, , OR-Tools, DOcplex
- **Institution:** [FEUP](https://sigarra.up.pt/feup/en/web_page.Inicial)
- **Course:** [CLP](https://sigarra.up.pt/feup/en/ucurr_geral.ficha_uc_view?pv_ocorrencia_id=486262) (Constraint Logic Programming)
- **Project grade:** ?/20
- **Group members:**
    - [Daniel Monteiro](https://github.com/dfamonteiro) (<up201806185@edu.fe.up.pt>)
    - [Rafael Soares Ribeiro](https://github.com/up201806330) (<up201806330@fe.up.pt>)

## Instalation
### Python packages
`pip3 install cplex docplex ortools`

### CPLEX
An instalation of CPLEX Studio must also be present. Our version is configured with Ubuntu's default installation location '/opt/ibm/ILOG/CPLEX_Studio201/cpoptimizer/bin/x86-64_linux/cpoptimizer'. 
Override this path with the cli argument '-execfile'

## Usage
### CLI
```console
➜  Container-Stacking-Problem git:(main) ✗ python3 main.py -h
usage: main.py [-h] -solver --solver-package [-path --input-path] [-benchmark [--benchmark-runs]] [-time [--max-time]] [-execfile [--cplex-execfile]]

Run the solver for the Container Stacking Problem

optional arguments:
  -h, --help            show this help message and exit
  -solver --solver-package
                        choice of solver to solve input problem. Currently supports 'ortools' and 'cplex'
  -path --input-path    the path to the file with the input problem (.json). By default is 'inputs/input.json'
  -benchmark [--benchmark-runs]
                        number of runs for benchmarking time (recommended: 5)
  -time [--max-time]    time limit (in seconds) to return solution. May return sub-optimal solution, or none at all
  -execfile [--cplex-execfile]
                        path for the CPLEX engine's executable. By default is '/opt/ibm/ILOG/CPLEX_Studio201/cpoptimizer/bin/x86-64_linux/cpoptimizer'
```

The cli options `-benchmark` and `-time` allow for benchmarking, and are used in the developed scripts:

### Test scripts
`multiple_runs.sh` runs and writes to `results.txt` output of an average of 5 runs, for each problem indexed 0 to 9, of both solvers.
`multiple_times.sh` runs and writes to `results.txt` output of the execution on a test file with increasing solve time cut offs, for both solvers. 
Was not used in final report due to missing functionality, not implemented due to lack of time to devote to the project.
