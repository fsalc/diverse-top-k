from pathlib import Path

import numpy as np

import duckdb as d

from ranking_refinements.query import Query, Condition
from ranking_refinements.experiments import Constraints, Constraint, Group, UsefulMethod, Query, Condition, Experiment, \
    ExperimentsRunner

d.sql(f"PRAGMA memory_limit='8GB';")
d.sql(f"PRAGMA threads=1;")

EXPERIMENTS = [
    {
        "name": "SF_MEPS",
        "dataset": "MEPS",
        "query_label": "data_size",
        "query": Query('meps.csv', label='150'). \
            where(
            Condition('AGE16X', '>=', 25),
            Condition('FAMS1231', '>=', 4),
        ).order_by("rank"),
        "constraints": Constraints(
            # Constraint(Group("race", "Black"), (20, 3)),
            Constraint(Group("SEX", 1), (10, 5)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
        "k_list": [10],
    },
    {
        "name": "SF_MEPS_200",
        "dataset": "MEPS",
        "query_label": "data_size",
        "query": Query('synthesized/meps/meps_200mb.csv', label='200'). \
            where(
            Condition('AGE16X', '>=', 25),
            Condition('FAMS1231', '>=', 4),
        ).order_by("rank", is_desc=False),
        "constraints": Constraints(
            # Constraint(Group("race", "Black"), (20, 3)),
            Constraint(Group("SEX", 1), (10, 5)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
        "k_list": [10],
    },
    {
        "name": "SF_MEPS_300",
        "dataset": "MEPS",
        "query_label": "data_size",
        "query": Query('synthesized/meps/meps_300mb.csv', label='300'). \
            where(
            Condition('AGE16X', '>=', 25),
            Condition('FAMS1231', '>=', 4),
        ).order_by("rank", is_desc=False),
        "constraints": Constraints(
            # Constraint(Group("race", "Black"), (20, 3)),
            Constraint(Group("SEX", 1), (10, 5)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
        "k_list": [10],
    },
    {
        "name": "SF_MEPS_400",
        "dataset": "MEPS",
        "query_label": "data_size",
        "query": Query('synthesized/meps/meps_400mb_test.csv', label='400'). \
            where(
            Condition('AGE16X', '>=', 25),
            Condition('FAMS1231', '>=', 4),
        ).order_by("rank", is_desc=False),
        "constraints": Constraints(
            # Constraint(Group("race", "Black"), (20, 3)),
            Constraint(Group("SEX", 1), (10, 5)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
        "k_list": [10],
    },
    {
        "name": "SF_MEPS_500",
        "dataset": "MEPS",
        "query_label": "data_size",
        "query": Query('synthesized/meps/meps_500mb.csv', label='500'). \
            where(
            Condition('AGE16X', '>=', 25),
            Condition('FAMS1231', '>=', 4),
        ).order_by("rank", is_desc=False),
        "constraints": Constraints(
            # Constraint(Group("race", "Black"), (20, 3)),
            Constraint(Group("SEX", 1), (10, 5)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
        "k_list": [10],
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
                        k_list=experiment['k_list']
                        )
        exprs.append(ex)

    runner = ExperimentsRunner(exprs, Path("experiments", 'SF', 'meps'), iterations=5)
    runner.run()