from pathlib import Path

import numpy as np

from ranking_refinements.fair import RefinementMethod
from ranking_refinements.query import Query, Condition
from ranking_refinements.experiments import Constraints, Constraint, Group, UsefulMethod, Query, Condition, Experiment, \
    ExperimentsRunner
import duckdb as d

d.sql(f"PRAGMA memory_limit='25GB';")
d.sql(f"PRAGMA threads=1;")

EXPERIMENTS = [
        {
        "name": "K_JAC_Law",
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
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.JACCARD_DISTANCE],
        "k_list": range(10, 101, 10),
        "algorithms": [RefinementMethod.MILP_OPT],
    },
        {
            "name": "K_JAC_Astronauts",
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
            "max_deviations": [0.5],
            "useful_methods": [UsefulMethod.JACCARD_DISTANCE],
            "algorithms": [RefinementMethod.MILP_OPT],
            "k_list": range(10, 101, 10),
        },
    {
        "name": "K_JAC_MEPS",
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
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.JACCARD_DISTANCE],
        "algorithms": [RefinementMethod.MILP_OPT],
        "k_list": range(10, 101, 10),
    },
    {
        "name": "K_JAC_TPCH",
        "dataset": "TPCH",
        "query": Query('TPCH/lineitem.csv'). \
            where(
            Condition('DISCOUNT', '>=', 0.05),
            Condition('DISCOUNT', '<=', 0.07),
            Condition('QUANTITY', '<', 20),
        ).order_by("revenue", is_desc=True),
        "constraints": Constraints(
            Constraint(Group("LINESTATUS", 'O'), (3, 1)),
            Constraint(Group("SHIPMODE", 'MAIL'), (10, 1)),
            Constraint(Group("RETURNFLAG", 'R'), (4, 1)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.JACCARD_DISTANCE],
        "algorithms": [RefinementMethod.MILP_OPT],
        "k_list": range(10, 101, 10),
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
                        k_list=experiment['k_list']
                        )
        exprs.append(ex)

    runner = ExperimentsRunner(exprs, Path("experiments", 'K', 'jaccard'), [("duration[sec]", "K"), ("deviation", "K")],
                               iterations=5)
    runner.run()
