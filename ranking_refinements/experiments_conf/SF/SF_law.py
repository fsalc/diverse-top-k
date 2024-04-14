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
        "name": "SF_Law_Students",
        "dataset": "law_students",
        "query": Query('law_students.csv', label='960'). \
            where(
            Condition('region_first', '=', 'GL'),
            Condition('UGPA', '>=', 3.5),
            Condition('UGPA', '<=', 4.0),
        ).order_by("LSAT", is_desc=True),
        "constraints": Constraints(
            # Constraint(Group("race", "Black"), (20, 3)),
            Constraint(Group("sex", 1), (10, 5)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
        "k_list": [10],
    },
    {
        "name": "SF_Law_Students-2MB",
        "dataset": "Law_Students-2MB",
        "query": Query('synthesized/law/law_students_2mb.csv', label='2000'). \
            where(
            Condition('region_first', '=', 'GL'),
            Condition('UGPA', '>=', 3.5),
            Condition('UGPA', '<=', 4.0),
        ).order_by("LSAT", is_desc=True),
        "constraints": Constraints(
            # Constraint(Group("race", "Black"), (20, 3)),
            Constraint(Group("sex", 1), (10, 5)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
        "k_list": [10],
    },
    {
        "name": "SF_Law_Students-3MB",
        "dataset": "Law_Students-3MB",
        "query": Query('synthesized/law/law_students_3mb.csv', label='3000'). \
            where(
            Condition('region_first', '=', 'GL'),
            Condition('UGPA', '>=', 3.5),
            Condition('UGPA', '<=', 4.0),
        ).order_by("LSAT", is_desc=True),
        "constraints": Constraints(
            # Constraint(Group("race", "Black"), (20, 3)),
            Constraint(Group("sex", 1), (10, 5)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
        "k_list": [10],
    },
    {
        "name": "SF_Law_Students-4MB",
        "dataset": "Law_Students-4MB",
        "query": Query('synthesized/law/law_students_4mb.csv', label='4000'). \
            where(
            Condition('region_first', '=', 'GL'),
            Condition('UGPA', '>=', 3.5),
            Condition('UGPA', '<=', 4.0),
        ).order_by("LSAT", is_desc=True),
        "constraints": Constraints(
            # Constraint(Group("race", "Black"), (20, 3)),
            Constraint(Group("sex", 1), (10, 5)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
        "k_list": [10],
    },
    {
        "name": "SF_Law_Students-5MB",
        "dataset": "Law_Students-5MB",
        "query": Query('synthesized/law/law_students_5mb.csv', label='5000'). \
            where(
            Condition('region_first', '=', 'GL'),
            Condition('UGPA', '>=', 3.5),
            Condition('UGPA', '<=', 4.0),
        ).order_by("LSAT", is_desc=True),
        "constraints": Constraints(
            # Constraint(Group("race", "Black"), (20, 3)),
            Constraint(Group("sex", 1), (10, 5)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
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
                        k_list=experiment['k_list']
                        )
        exprs.append(ex)

    runner = ExperimentsRunner(exprs, Path("experiments", 'SF', 'law'), iterations=5)
    runner.run()
