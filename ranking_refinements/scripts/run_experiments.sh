echo 'Dry run...'
# echo 'Running algorithm comparisons...';
# for EXPERIMENT in ./experiments_conf/algorithm/*.py; do
#     python3 $EXPERIMENT
# done;

# echo 'Running constraint bounds comparisons...';
# for EXPERIMENT in ./experiments_conf/constraints/constraints_bounds/*.py; do
#     python3 $EXPERIMENT
# done;

# echo 'Running number of constraints comparisons...';
# for EXPERIMENT in ./experiments_conf/constraints/number_of_constraints/*.py; do
#     python3 $EXPERIMENT
# done;

# echo 'Running k* comparisons...';
# for EXPERIMENT in ./experiments_conf/k/*.py; do
#     python3 $EXPERIMENT
# done;

# echo 'Running epsilon (maximum average deviation) comparisons...';
# for EXPERIMENT in ./experiments_conf/max_dev/*.py; do
#     python3 $EXPERIMENT
# done;

# echo 'Running predicate type comparisons...';
# for EXPERIMENT in ./experiments_conf/predicate/*.py; do
#     python3 $EXPERIMENT
# done;

# echo 'Running data size comparisons...';
# for EXPERIMENT in ./experiments_conf/predicate/SF_astronauts.py ./experiments_conf/predicate/SF_law.py ./experiments_conf/predicate/SF_meps.py ./experiments_conf/predicate/SF_q5.py; do
#     python3 $EXPERIMENT
# done;