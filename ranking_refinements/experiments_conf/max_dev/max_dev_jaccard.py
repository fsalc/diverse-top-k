from pathlib import Path

import numpy as np

from ranking_refinements.query import Query, Condition
from ranking_refinements.experiments import Constraints, Constraint, Group, UsefulMethod, Query, Condition, Experiment, \
    ExperimentsRunner
import duckdb as d

d.sql(f"PRAGMA memory_limit='25GB';")
d.sql(f"PRAGMA threads=1;")

EXPERIMENTS = [
    {
        "name": "MaxDev_JAC_Law",
        "dataset": "law_students",
        "query": Query('law_students.csv'). \
            where(
            Condition('region_first', '=', 'GL'),
            Condition('UGPA', '>=', 3.5),
            Condition('UGPA', '<=', 4.0),
        ).order_by("LSAT", is_desc=True),
        "constraints": Constraints(
            # Constraint(Group("race", "Black"), (20, 3)),
            Constraint(Group("sex", 1), (30, 15)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": np.arange(0.0, 1.1, 0.1),
        "useful_methods": [UsefulMethod.JACCARD_DISTANCE],
        "k_list": [10]
    },
        {
            "name": "MaxDev_JAC_Astronauts",
            "dataset": "astronauts",
            "query": Query('astronauts.csv'). \
                where(
                Condition('Graduate Major', '=', 'Physics'),
                Condition('Space Walks', '>=', 1),
                Condition('Space Walks', '<=', 3),
            ).order_by("Space Flight (hr)", is_desc=True),
            "constraints": Constraints(
                Constraint(Group("Gender", "Female"), (10, 5))
            ),
            "only_lower_bound_constraints": True,
            "max_deviations": np.arange(0.0, 1.1, 0.1),
            "useful_methods": [UsefulMethod.JACCARD_DISTANCE],
            "k_list": [10]
        },
    {
        "name": "MaxDev_JAC_MEPS",
        "dataset": "MEPS",
        "query": Query('meps.csv'). \
            where(
            Condition('AGE16X', '>=', 25),
            Condition('FAMS1231', '>=', 4),
        ).order_by("rank", is_desc=True),
        "constraints": Constraints(
            # Constraint(Group("race", "Black"), (20, 3)),
            Constraint(Group("SEX", 1), (30, 15)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": np.arange(0.0, 1.1, 0.1),
        "useful_methods": [UsefulMethod.JACCARD_DISTANCE],
        "k_list": [10]
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
                        k_list=experiment['k_list']
                        )
        exprs.append(ex)

    runner = ExperimentsRunner(exprs, Path("experiments", 'max_dev', 'jaccard'),
                               [("duration[sec]", "max_deviation"), ("deviation", "max_deviation")],
                               iterations=5)
    runner.run()
