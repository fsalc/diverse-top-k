from pathlib import Path

import numpy as np

import duckdb as d

from ranking_refinements.query import Query, Condition
from ranking_refinements.experiments import Constraints, Constraint, Group, UsefulMethod, Query, Condition, Experiment, \
    ExperimentsRunner

d.sql(f"PRAGMA memory_limit='100GB';")
d.sql(f"PRAGMA threads=1;")

# Query  2.4.12.2
EXPERIMENTS = [
    {
        "name": "SF_Q2-4-12-2_TPCH_SF1",
        "dataset": "TPCH_SF-1",
        # l.commitdate < l.receiptdate and
        # l.shipdate < l.commitdate and
        "query": Query(['TPCH/SCALE-1/lineitem.csv']). \
        join('TPCH/SCALE-1/orders.csv', 'o.ORDERKEY = ORDERKEY'). \
            where(
            Condition('SHIPDATE', '>=', 757382400),
            Condition('SHIPDATE', '<', 788918400),
            Condition('SHIPMODE', 'IN', ['MAIL', 'SHIP']),
        ).order_by("REVENUE1", is_desc=True),
        "constraints": Constraints(
            Constraint(Group("LINESTATUS", 'O'), (3, 1)),
            Constraint(Group("LINESTATUS", 'F'), (3, 1)),
            # Constraint(Group("l.SHIPMODE", 'MAIL'), (10, 1)),
            Constraint(Group("RETURNFLAG", 'R'), (4, 1)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
        "k_list": [10],
    },
{
        "name": "SF_Q2-4-12-2_TPCH_SF10",
        "dataset": "TPCH_SF-10",
        # l.commitdate < l.receiptdate and
        # l.shipdate < l.commitdate and
        "query": Query(['TPCH/SCALE-10/lineitem.csv']). \
        join('TPCH/SCALE-10/orders.csv', 'o.ORDERKEY = ORDERKEY'). \
            where(
            Condition('SHIPDATE', '>=', 757382400),
            Condition('SHIPDATE', '<', 788918400),
            Condition('SHIPMODE', 'IN', ['MAIL', 'SHIP']),
        ).order_by("REVENUE1", is_desc=True),
        "constraints": Constraints(
            Constraint(Group("LINESTATUS", 'O'), (3, 1)),
            Constraint(Group("LINESTATUS", 'F'), (3, 1)),
            # Constraint(Group("l.SHIPMODE", 'MAIL'), (10, 1)),
            Constraint(Group("RETURNFLAG", 'R'), (4, 1)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
        "k_list": [10],
    },
{
        "name": "SF_Q2-4-12-2_TPCH_SF1",
        "dataset": "TPCH_SF-30",
        # l.commitdate < l.receiptdate and
        # l.shipdate < l.commitdate and
        "query": Query(['TPCH/SCALE-30/lineitem.csv']). \
        join('TPCH/SCALE-30/orders.csv', 'o.ORDERKEY = ORDERKEY'). \
            where(
            Condition('SHIPDATE', '>=', 757382400),
            Condition('SHIPDATE', '<', 788918400),
            Condition('SHIPMODE', 'IN', ['MAIL', 'SHIP']),
        ).order_by("REVENUE1", is_desc=True),
        "constraints": Constraints(
            Constraint(Group("LINESTATUS", 'O'), (3, 1)),
            Constraint(Group("LINESTATUS", 'F'), (3, 1)),
            # Constraint(Group("l.SHIPMODE", 'MAIL'), (10, 1)),
            Constraint(Group("RETURNFLAG", 'R'), (4, 1)),
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

    runner = ExperimentsRunner(exprs, Path("experiments", 'SF', 'Q2-4-12-2'), iterations=5)
    runner.run()
