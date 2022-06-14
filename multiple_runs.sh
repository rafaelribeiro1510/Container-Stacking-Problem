#!/bin/bash

runs=0
solvers=(ortools cplex)
test_file="inputs/constantContainers_"

for solver in "${solvers[@]}"; do
    for size in {0..9}; do
        echo "-benchmark ${runs} -solver ${solver} -path ${test_file}${size}"
        echo $(python3 main.py -benchmark $runs -solver $solver -path $test_file$size) >> results.txt
    done
done