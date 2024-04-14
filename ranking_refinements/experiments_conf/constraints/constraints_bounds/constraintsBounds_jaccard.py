from pathlib import Path

from ranking_refinements.fair import RefinementMethod
from ranking_refinements.experiments import Constraints, Constraint, Group, UsefulMethod, Query, Condition, Experiment, \
    ExperimentsRunner
import duckdb as d

d.sql(f"PRAGMA memory_limit='25GB';")
d.sql(f"PRAGMA threads=1;")

EXPERIMENTS = [
    {
        "name": "ConstraintsBounds_JAC_Law",
        "dataset": "law_students",
        "query": Query('law_students.csv'). \
            where(
            Condition('region_first', '=', 'GL'),
            Condition('UGPA', '>=', 3.5),
            Condition('UGPA', '<=', 4.0),
        ).order_by("LSAT", is_desc=True),
        "constraints": [
            Constraints(
                Constraint(Group("sex", 1), (2, 1)),
                Constraint(Group("sex", 2), (2, 1)),
                label="LowerBound"
            ),
            Constraints(
                Constraint(Group("sex", 1), (2, 1)),
                Constraint(Group("sex", 2), (2, 1), sense='U'),
                label="Combined"
            )
        ],
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.JACCARD_DISTANCE],
        "algorithms": [RefinementMethod.MILP_OPT],
        "k_list": [10],
    },
    {
        "name": "ConstraintsBounds_JAC_Astronauts",
        "dataset": "astronauts",
        "query": Query('astronauts.csv'). \
            where(
            Condition('Graduate Major', '=', 'Physics'),
            Condition('Space Walks', '>=', 1),
            Condition('Space Walks', '<=', 3),
        ).order_by("Space Flight (hr)", is_desc=True),
        "constraints": [
            Constraints(
                Constraint(Group("Gender", "Female"), (2, 1)),
                Constraint(Group("Gender", "Male"), (2, 1)),
                label="LowerBound"
            ),
            Constraints(
                Constraint(Group("Gender", "Female"), (2, 1)),
                Constraint(Group("Gender", "Male"), (2, 1), sense='U'),
                label="Combined"
            )
        ],
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.JACCARD_DISTANCE],
        "algorithms": [RefinementMethod.MILP_OPT],
        "k_list": [10],
    },
    {
        "name": "ConstraintsBounds_JAC_MEPS",
        "dataset": "MEPS",
        "query": Query('meps.csv'). \
            where(
            Condition('AGE16X', '>=', 25),
            Condition('FAMS1231', '>=', 4),
        ).order_by("rank", is_desc=True),
        "constraints": [
            Constraints(
                Constraint(Group("SEX", 1), (2, 1)),
                Constraint(Group("SEX", 2), (2, 1)),
                label="LowerBound"
            ),
            Constraints(
                Constraint(Group("SEX", 1), (2, 1)),
                Constraint(Group("SEX", 2), (2, 1), sense='U'),
                label="Combined"
            )
        ],
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.JACCARD_DISTANCE],
        "algorithms": [RefinementMethod.MILP_OPT],
        "k_list": [10],
    },
]
if __name__ == '__main__':
    exprs = []
    for experiment in EXPERIMENTS:
        ex = Experiment(experiment['name'],
                        experiment['dataset'],
                        experiment['query'],
                        experiment['constraints'],
                        only_lower_bound_constraints=experiment['only_lower_bound_constraints'],
                        max_deviations=experiment['max_deviations'],
                        useful_methods=experiment['useful_methods'],
                        algorithms=experiment['algorithms'],
                        k_list=experiment['k_list'],
                        constraints_label="constraints_bounds"
                        )
        exprs.append(ex)

    runner = ExperimentsRunner(exprs, Path("experiments", 'constraints_bounds', 'jaccard'),
                               [("total_duration[sec]", "algorithm"), ("deviation", "algorithm")],
                               iterations=10)
    runner.run()
