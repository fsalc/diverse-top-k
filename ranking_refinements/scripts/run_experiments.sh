# echo "Dry run..."
echo "Running algorithm comparisons...";
for EXPERIMENT in ./experiments_conf/algorithm/*.py; do
    echo "Executing $EXPERIMENT...";
    python3 $EXPERIMENT;
done;

echo "Running constraint bounds comparisons...";
for EXPERIMENT in ./experiments_conf/constraints/constraints_bounds/*.py; do
    echo "Executing $EXPERIMENT...";
    python3 $EXPERIMENT;
done;

echo "Running number of constraints comparisons...";
for EXPERIMENT in ./experiments_conf/constraints/number_of_constraints/*.py; do
    echo "Executing $EXPERIMENT...";
    python3 $EXPERIMENT;
done;

echo "Running k* comparisons...";
for EXPERIMENT in ./experiments_conf/k/*.py; do
    echo "Executing $EXPERIMENT...";
    python3 $EXPERIMENT;
done;

echo "Running epsilon (maximum average deviation) comparisons...";
for EXPERIMENT in ./experiments_conf/max_dev/*.py; do
    echo "Executing $EXPERIMENT...";
    python3 $EXPERIMENT;
done;

echo "Running predicate type comparisons...";
for EXPERIMENT in ./experiments_conf/predicate/*.py; do
    echo "Executing $EXPERIMENT...";
    python3 $EXPERIMENT;
done;

echo "Running data size comparisons...";
for EXPERIMENT in ./experiments_conf/SF/SF_astronauts.py ./experiments_conf/SF/SF_law.py ./experiments_conf/SF/SF_meps.py ./experiments_conf/SF/SF_q5.py; do
    echo "Executing $EXPERIMENT...";
    python3 $EXPERIMENT;
done;