#!/bin/bash

runs=5
solvers=(ortools cplex)
test_file="inputs/constantContainers_"

for solver in "${solvers[@]}"; do
    for index in {0..9}; do
        echo $(python3 main.py -benchmark $runs -solver $solver -path $test_file$index) >> results.txt
    done
done