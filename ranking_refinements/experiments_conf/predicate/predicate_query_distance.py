from pathlib import Path

import numpy as np

import duckdb as d

from ranking_refinements.query import Query, Condition
from ranking_refinements.experiments import Constraints, Constraint, Group, UsefulMethod, Query, Condition, Experiment, \
    ExperimentsRunner

d.sql(f"PRAGMA memory_limit='25GB';")
d.sql(f"PRAGMA threads=1;")

EXPERIMENTS = [
    {
        "name": "Predicate_QD_Law",
        "dataset": "law_students",
        "query": [
            Query('law_students.csv').
            where(
                Condition('region_first', '=', 'GL'),
            ).order_by("LSAT", is_desc=True).
            set_label("Categorical"),
            Query('law_students.csv').
            where(
                Condition('UGPA', '>=', 4.0),
            ).order_by("LSAT", is_desc=True).
            set_label("Numerical"),
        ],
        "constraints": Constraints(
            Constraint(Group("sex", 1), (2, 1)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.QUERY_DISTANCE],
        "k_list": [10],
    },
    {
        "name": "Predicate_QD_Astronauts",
        "dataset": "astronauts",
        "query": [
            Query('astronauts.csv').
                where(
                Condition('Graduate Major', '=', 'Physics'),
            ).order_by("Space Flight (hr)", is_desc=True).
                set_label("Categorical"),
            Query('astronauts.csv').
                where(
                Condition('Space Walks', '<=', 4),
            ).order_by("Space Flight (hr)", is_desc=True).
                set_label("Numerical"),
        ],
        "constraints": Constraints(
            Constraint(Group("Gender", "Female"), (2, 1))
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.QUERY_DISTANCE],
        "k_list": [10],
    },
    # {
    #     "name": "Predicate_QD_MEPS",
    #     "dataset": "MEPS",
    #     "query": Query('meps.csv'). \
    #         where(
    #         Condition('AGE16X', '>=', 25),
    #         Condition('FAMS1231', '>=', 4),
    #     ).order_by("rank", is_desc=True),
    #     "constraints": Constraints(
    #         # Constraint(Group("race", "Black"), (20, 3)),
    #         Constraint(Group("SEX", 1), (30, 15)),
    #     ),
    #     "only_lower_bound_constraints": True,
    #     "max_deviations": [0.5],
    #     "useful_methods": [UsefulMethod.KENDALL_DISTANCE],
    #     "k_list": range(10, 101, 10),
    # },
    # {
    #     "name": "K_Ken_TPCH",
    #     "dataset": "TPCH",
    #     "query": Query('TPCH/lineitem.csv'). \
    #         where(
    #         Condition('DISCOUNT', '>=', 0.05),
    #         Condition('DISCOUNT', '<=', 0.07),
    #         Condition('QUANTITY', '<', 20),
    #     ).order_by("revenue", is_desc=True),
    #     "constraints": Constraints(
    #         Constraint(Group("LINESTATUS", 'O'), (3, 1)),
    #         Constraint(Group("SHIPMODE", 'MAIL'), (10, 1)),
    #         Constraint(Group("RETURNFLAG", 'R'), (4, 1)),
    #     ),
    #     "only_lower_bound_constraints": True,
    #     "max_deviations": [0.5],
    #     "useful_methods": [UsefulMethod.QUERY_DISTANCE],
    #     "k_list": range(10, 101, 10),
    # },
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
                        k_list=experiment['k_list'],
                        query_label="predicate_type"
                        )
        exprs.append(ex)

    runner = ExperimentsRunner(exprs, Path("experiments", 'Predicate', 'query_distance'), [("duration[sec]", "K"), ("deviation", "K")],
                               iterations=5)
    runner.run()
