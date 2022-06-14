#!/bin/bash

runs=0
solvers=(ortools cplex)
timestamps=(0.1 0.2 0.5 1 1.1 1.2 1.3 1.4 1.5 2)
test_file="inputs/constantContainers_0"

for solver in "${solvers[@]}"; do
    for time in "${timestamps[@]}"; do
        echo "-benchmark ${runs} -solver ${solver} -path ${test_file} -time ${time}"
        echo $(python3 main.py -benchmark ${runs} -solver ${solver} -path ${test_file} -time ${time}) >> results.txt
    done
done