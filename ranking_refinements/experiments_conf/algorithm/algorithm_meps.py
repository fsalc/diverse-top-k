from pathlib import Path

import numpy as np
import os

from ranking_refinements.fair import RefinementMethod
from ranking_refinements.experiments import Constraints, Constraint, Group, UsefulMethod, Query, Condition, Experiment, ExperimentsRunner
import duckdb as d

d.sql(f"PRAGMA memory_limit='280GB';")
d.sql(f"PRAGMA threads=1;")

EXPERIMENTS = [
    {
        "name": "ALG_CombUseful_MEPS",
        "dataset": "MEPS",
        "query": Query('meps.csv'). \
            where(
            Condition('AGE16X', '>=', 25),
            Condition('FAMS1231', '>=', 4),
        ).order_by("rank"),
        "constraints": Constraints(
            # Constraint(Group("race", "Black"), (20, 3)),
            Constraint(Group("SEX", 1), (30, 15)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL, UsefulMethod.KENDALL_DISTANCE],
        "algorithms": [RefinementMethod.MILP_OPT, RefinementMethod.MILP, RefinementMethod.BRUTE_PROV, RefinementMethod.BRUTE],
        "k_list": [10],
        "comparison_criteria": [("runtime [sec]", "algorithm"), ("deviation", "algorithm")],
        "iterations": 10
    }
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
                        k_list=experiment['k_list']
                        )
        exprs.append(ex)

    runner = ExperimentsRunner(exprs, Path("experiments", 'algorithm', 'meps'),
                               [("duration[sec]", "algorithm"), ("deviation", "algorithm")],
                               iterations=5)
    runner.run()
