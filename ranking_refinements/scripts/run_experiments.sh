#!/bin/bash

PURPLE='\033[0;35m'
RED='\033[0;31m'
NORMAL='\033[0m'

# echo -e "${PURPLE}Dry run...${NORMAL}"
if [[ "$RUN_ALL" == "TRUE" || "$RUN_ALGORITHM" == "TRUE" ]]
then
    echo -e "${PURPLE}$(date)\tRunning algorithm comparisons...${NORMAL}";
    for EXPERIMENT in ./experiments_conf/algorithm/*.py; do
        echo -e "${PURPLE}$(date)\tExecuting $EXPERIMENT...${NORMAL}";
        python3 $EXPERIMENT;
    done;
else
    echo -e "${RED}$(date)\tSkipping algorithm comparisons...${NORMAL}";
fi

if [[ "$RUN_ALL" == "TRUE" || "$RUN_CONSTRAINT_BOUNDS" == "TRUE" ]]
then
    echo -e "${PURPLE}$(date)\tRunning constraint bounds comparisons...${NORMAL}";
    for EXPERIMENT in ./experiments_conf/constraints/constraints_bounds/*.py; do
        echo -e "${PURPLE}$(date)\tExecuting $EXPERIMENT...${NORMAL}";
        python3 $EXPERIMENT;
    done;
else
    echo -e "${RED}$(date)\tSkipping constraint bounds comparisons...${NORMAL}";
fi

if [[ "$RUN_ALL" == "TRUE" || "$RUN_CONSTRAINTS_NUMBER" == "TRUE" ]]
then
    echo -e "${PURPLE}$(date)\tRunning number of constraints comparisons...${NORMAL}";
    for EXPERIMENT in ./experiments_conf/constraints/number_of_constraints/*.py; do
        echo -e "${PURPLE}$(date)\tExecuting $EXPERIMENT...${NORMAL}";
        python3 $EXPERIMENT;
    done;
else
    echo -e "${RED}$(date)\tSkipping number of constraints comparisons...${NORMAL}";
fi

if [[ "$RUN_ALL" == "TRUE" || "$RUN_K_STAR" == "TRUE" ]]
then
    echo -e "${PURPLE}$(date)\tRunning k* comparisons...${NORMAL}";
    for EXPERIMENT in ./experiments_conf/k/*.py; do
        echo -e "${PURPLE}$(date)\tExecuting $EXPERIMENT...${NORMAL}";
        python3 $EXPERIMENT;
    done;
else
    echo -e "${RED}$(date)\tSkipping k* comparisons...${NORMAL}";
fi

if [[ "$RUN_ALL" == "TRUE" || "$RUN_EPSILON" == "TRUE" ]]
then
    echo -e "${PURPLE}$(date)\tRunning epsilon (maximum average deviation) comparisons...${NORMAL}";
    for EXPERIMENT in ./experiments_conf/max_dev/*.py; do
        echo -e "${PURPLE}$(date)\tExecuting $EXPERIMENT...${NORMAL}";
        python3 $EXPERIMENT;
    done;
else
    echo -e "${RED}$(date)\tSkipping epsilon (maximum average deviation) comparisons...${NORMAL}";
fi

if [[ "$RUN_ALL" == "TRUE" || "$RUN_PREDICATE_TYPE" == "TRUE" ]]
then
    echo -e "${PURPLE}$(date)\tRunning predicate type comparisons...${NORMAL}";
    for EXPERIMENT in ./experiments_conf/predicate/*.py; do
        echo -e "${PURPLE}$(date)\tExecuting $EXPERIMENT...${NORMAL}";
        python3 $EXPERIMENT;
    done;
else
    echo -e "${RED}$(date)\tSkipping predicate type comparisons...${NORMAL}";
fi

if [[ "$RUN_ALL" == "TRUE" || "$RUN_DATA_SIZE" == "TRUE" ]]
then
    echo -e "${PURPLE}$(date)\tRunning data size comparisons...${NORMAL}";
    for EXPERIMENT in ./experiments_conf/SF/SF_astronauts.py ./experiments_conf/SF/SF_law.py ./experiments_conf/SF/SF_meps.py ./experiments_conf/SF/SF_q5.py; do
        echo -e "${PURPLE}$(date)\tExecuting $EXPERIMENT...${NORMAL}";
        python3 $EXPERIMENT;
    done;
else
    echo -e "${RED}$(date)\tSkipping data size comparisons...${NORMAL}";
fi