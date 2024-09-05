PURPLE='\033[0;35m'
NORMAL='\033[0m'

# echo -e "${PURPLE}Dry run...${NORMAL}"
echo -e "Running algorithm comparisons...";
for EXPERIMENT in ./experiments_conf/algorithm/*.py; do
    echo -e "${PURPLE}Executing $EXPERIMENT...${NORMAL}";
    python3 $EXPERIMENT;
done;

echo -e "Running constraint bounds comparisons...";
for EXPERIMENT in ./experiments_conf/constraints/constraints_bounds/*.py; do
    echo -e "${PURPLE}Executing $EXPERIMENT...${NORMAL}";
    python3 $EXPERIMENT;
done;

echo -e "Running number of constraints comparisons...";
for EXPERIMENT in ./experiments_conf/constraints/number_of_constraints/*.py; do
    echo -e "${PURPLE}Executing $EXPERIMENT...${NORMAL}";
    python3 $EXPERIMENT;
done;

echo -e "Running k* comparisons...";
for EXPERIMENT in ./experiments_conf/k/*.py; do
    echo -e "${PURPLE}Executing $EXPERIMENT...${NORMAL}";
    python3 $EXPERIMENT;
done;

echo -e "Running epsilon (maximum average deviation) comparisons...";
for EXPERIMENT in ./experiments_conf/max_dev/*.py; do
    echo -e "${PURPLE}Executing $EXPERIMENT...${NORMAL}";
    python3 $EXPERIMENT;
done;

echo -e "Running predicate type comparisons...";
for EXPERIMENT in ./experiments_conf/predicate/*.py; do
    echo -e "${PURPLE}Executing $EXPERIMENT...${NORMAL}";
    python3 $EXPERIMENT;
done;

echo -e "Running data size comparisons...";
for EXPERIMENT in ./experiments_conf/SF/SF_astronauts.py ./experiments_conf/SF/SF_law.py ./experiments_conf/SF/SF_meps.py ./experiments_conf/SF/SF_q5.py; do
    echo -e "${PURPLE}Executing $EXPERIMENT...${NORMAL}";
    python3 $EXPERIMENT;
done;