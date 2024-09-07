from pathlib import Path

import numpy as np

import duckdb as d

from ranking_refinements.query import Query, Condition
from ranking_refinements.experiments import Constraints, Constraint, Group, UsefulMethod, Query, Condition, Experiment, \
    ExperimentsRunner

d.sql(f"PRAGMA memory_limit='8GB';")
d.sql(f"PRAGMA threads=1;")

# Query  5
EXPERIMENTS = [
    {
        "name": "SF_Q5_TPCH_SF1-10",
        "dataset": "TPC-H-100",
        "query_label": "data_size",
        "query": Query(['TPCH/SCALE-1/1/customer.csv'], label="100MB", verbatim='''SELECT c.*, o.*, l.*, s.*, n.*, re.* FROM "data/TPCH/SCALE-1/1/customer.csv" AS c JOIN "data/TPCH/SCALE-1/1/orders.csv" AS o ON o.CUSTKEY = c.CUSTKEY JOIN "data/TPCH/SCALE-1/1/lineitem.csv" AS l ON l.ORDERKEY = o.ORDERKEY JOIN "data/TPCH/SCALE-1/1/supplier.csv" AS s ON s.SUPPKEY = l.SUPPKEY JOIN "data/TPCH/SCALE-1/1/nation.csv" AS n ON n.NATIONKEY = s.NATIONKEY JOIN "data/TPCH/SCALE-1/1/region.csv" AS re ON re.REGIONKEY = n.REGIONKEY WHERE re.NAME = 'ASIA' ORDER BY l.REVENUE1 DESC'''),
        "constraints": Constraints(
            Constraint(Group("o.ORDERPRIORITY", "5-LOW"), (10, 5)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
        "k_list": [10],
    },
    {
        "name": "SF_Q5_TPCH_SF2-10",
        "dataset": "TPC-H-200",
        "query_label": "data_size",
        "query": Query(['TPCH/SCALE-1/2/customer.csv'], label="200MB", verbatim='''SELECT c.*, o.*, l.*, s.*, n.*, re.* FROM "data/TPCH/SCALE-1/2/customer.csv" AS c JOIN "data/TPCH/SCALE-1/2/orders.csv" AS o ON o.CUSTKEY = c.CUSTKEY JOIN "data/TPCH/SCALE-1/2/lineitem.csv" AS l ON l.ORDERKEY = o.ORDERKEY JOIN "data/TPCH/SCALE-1/2/supplier.csv" AS s ON s.SUPPKEY = l.SUPPKEY JOIN "data/TPCH/SCALE-1/2/nation.csv" AS n ON n.NATIONKEY = s.NATIONKEY JOIN "data/TPCH/SCALE-1/2/region.csv" AS re ON re.REGIONKEY = n.REGIONKEY WHERE re.NAME = 'ASIA' ORDER BY l.REVENUE1 DESC'''),
        "constraints": Constraints(
            Constraint(Group("o.ORDERPRIORITY", "5-LOW"), (10, 5)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
        "k_list": [10],
    },
    {
        "name": "SF_Q5_TPCH_SF3-10",
        "dataset": "TPC-H-300",
        "query_label": "data_size",
        "query": Query(['TPCH/SCALE-1/3/customer.csv'], label="300MB", verbatim='''SELECT c.*, o.*, l.*, s.*, n.*, re.* FROM "data/TPCH/SCALE-1/3/customer.csv" AS c JOIN "data/TPCH/SCALE-1/3/orders.csv" AS o ON o.CUSTKEY = c.CUSTKEY JOIN "data/TPCH/SCALE-1/3/lineitem.csv" AS l ON l.ORDERKEY = o.ORDERKEY JOIN "data/TPCH/SCALE-1/3/supplier.csv" AS s ON s.SUPPKEY = l.SUPPKEY JOIN "data/TPCH/SCALE-1/3/nation.csv" AS n ON n.NATIONKEY = s.NATIONKEY JOIN "data/TPCH/SCALE-1/3/region.csv" AS re ON re.REGIONKEY = n.REGIONKEY WHERE re.NAME = 'ASIA' ORDER BY l.REVENUE1 DESC'''),
        "constraints": Constraints(
            Constraint(Group("o.ORDERPRIORITY", "5-LOW"), (10, 5)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
        "k_list": [10],
    },
    {
        "name": "SF_Q5_TPCH_SF4-10",
        "dataset": "TPC-H-400",
        "query_label": "data_size",
        "query": Query(['TPCH/SCALE-1/4/customer.csv'], label="400MB", verbatim='''SELECT c.*, o.*, l.*, s.*, n.*, re.* FROM "data/TPCH/SCALE-1/4/customer.csv" AS c JOIN "data/TPCH/SCALE-1/4/orders.csv" AS o ON o.CUSTKEY = c.CUSTKEY JOIN "data/TPCH/SCALE-1/4/lineitem.csv" AS l ON l.ORDERKEY = o.ORDERKEY JOIN "data/TPCH/SCALE-1/4/supplier.csv" AS s ON s.SUPPKEY = l.SUPPKEY JOIN "data/TPCH/SCALE-1/4/nation.csv" AS n ON n.NATIONKEY = s.NATIONKEY JOIN "data/TPCH/SCALE-1/4/region.csv" AS re ON re.REGIONKEY = n.REGIONKEY WHERE re.NAME = 'ASIA' ORDER BY l.REVENUE1 DESC'''),
        "constraints": Constraints(
            Constraint(Group("o.ORDERPRIORITY", "5-LOW"), (10, 5)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
        "k_list": [10],
    },
    {
        "name": "SF_Q5_TPCH_SF5-10",
        "dataset": "TPC-H-500",
        "query_label": "data_size",
        "query": Query(['TPCH/SCALE-1/5/customer.csv'], label="500MB", verbatim='''SELECT c.*, o.*, l.*, s.*, n.*, re.* FROM "data/TPCH/SCALE-1/5/customer.csv" AS c JOIN "data/TPCH/SCALE-1/5/orders.csv" AS o ON o.CUSTKEY = c.CUSTKEY JOIN "data/TPCH/SCALE-1/5/lineitem.csv" AS l ON l.ORDERKEY = o.ORDERKEY JOIN "data/TPCH/SCALE-1/5/supplier.csv" AS s ON s.SUPPKEY = l.SUPPKEY JOIN "data/TPCH/SCALE-1/5/nation.csv" AS n ON n.NATIONKEY = s.NATIONKEY JOIN "data/TPCH/SCALE-1/5/region.csv" AS re ON re.REGIONKEY = n.REGIONKEY WHERE re.NAME = 'ASIA' ORDER BY l.REVENUE1 DESC'''),
        "constraints": Constraints(
            Constraint(Group("o.ORDERPRIORITY", "5-LOW"), (10, 5)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
        "k_list": [10],
    },
    {
        "name": "SF_Q5_TPCH_SF6-10",
        "dataset": "TPC-H-600",
        "query_label": "data_size",
        "query": Query(['TPCH/SCALE-1/6/customer.csv'], label="600MB", verbatim='''SELECT c.*, o.*, l.*, s.*, n.*, re.* FROM "data/TPCH/SCALE-1/6/customer.csv" AS c JOIN "data/TPCH/SCALE-1/6/orders.csv" AS o ON o.CUSTKEY = c.CUSTKEY JOIN "data/TPCH/SCALE-1/6/lineitem.csv" AS l ON l.ORDERKEY = o.ORDERKEY JOIN "data/TPCH/SCALE-1/6/supplier.csv" AS s ON s.SUPPKEY = l.SUPPKEY JOIN "data/TPCH/SCALE-1/6/nation.csv" AS n ON n.NATIONKEY = s.NATIONKEY JOIN "data/TPCH/SCALE-1/6/region.csv" AS re ON re.REGIONKEY = n.REGIONKEY WHERE re.NAME = 'ASIA' ORDER BY l.REVENUE1 DESC'''),
        "constraints": Constraints(
            Constraint(Group("o.ORDERPRIORITY", "5-LOW"), (10, 5)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
        "k_list": [10],
    },
    {
        "name": "SF_Q5_TPCH_SF7-10",
        "dataset": "TPC-H-700",
        "query_label": "data_size",
        "query": Query(['TPCH/SCALE-1/7/customer.csv'], label="700MB", verbatim='''SELECT c.*, o.*, l.*, s.*, n.*, re.* FROM "data/TPCH/SCALE-1/7/customer.csv" AS c JOIN "data/TPCH/SCALE-1/7/orders.csv" AS o ON o.CUSTKEY = c.CUSTKEY JOIN "data/TPCH/SCALE-1/7/lineitem.csv" AS l ON l.ORDERKEY = o.ORDERKEY JOIN "data/TPCH/SCALE-1/7/supplier.csv" AS s ON s.SUPPKEY = l.SUPPKEY JOIN "data/TPCH/SCALE-1/7/nation.csv" AS n ON n.NATIONKEY = s.NATIONKEY JOIN "data/TPCH/SCALE-1/7/region.csv" AS re ON re.REGIONKEY = n.REGIONKEY WHERE re.NAME = 'ASIA' ORDER BY l.REVENUE1 DESC'''),
        "constraints": Constraints(
            Constraint(Group("o.ORDERPRIORITY", "5-LOW"), (10, 5)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
        "k_list": [10],
    },
    {
        "name": "SF_Q5_TPCH_SF8-10",
        "dataset": "TPC-H-800",
        "query_label": "data_size",
        "query": Query(['TPCH/SCALE-1/8/customer.csv'], label="800MB", verbatim='''SELECT c.*, o.*, l.*, s.*, n.*, re.* FROM "data/TPCH/SCALE-1/8/customer.csv" AS c JOIN "data/TPCH/SCALE-1/8/orders.csv" AS o ON o.CUSTKEY = c.CUSTKEY JOIN "data/TPCH/SCALE-1/8/lineitem.csv" AS l ON l.ORDERKEY = o.ORDERKEY JOIN "data/TPCH/SCALE-1/8/supplier.csv" AS s ON s.SUPPKEY = l.SUPPKEY JOIN "data/TPCH/SCALE-1/8/nation.csv" AS n ON n.NATIONKEY = s.NATIONKEY JOIN "data/TPCH/SCALE-1/8/region.csv" AS re ON re.REGIONKEY = n.REGIONKEY WHERE re.NAME = 'ASIA' ORDER BY l.REVENUE1 DESC'''),
        "constraints": Constraints(
            Constraint(Group("o.ORDERPRIORITY", "5-LOW"), (10, 5)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
        "k_list": [10],
    },
    {
        "name": "SF_Q5_TPCH_SF9-10",
        "dataset": "TPC-H-900",
        "query_label": "data_size",
        "query": Query(['TPCH/SCALE-1/9/customer.csv'], label="900MB", verbatim='''SELECT c.*, o.*, l.*, s.*, n.*, re.* FROM "data/TPCH/SCALE-1/9/customer.csv" AS c JOIN "data/TPCH/SCALE-1/9/orders.csv" AS o ON o.CUSTKEY = c.CUSTKEY JOIN "data/TPCH/SCALE-1/9/lineitem.csv" AS l ON l.ORDERKEY = o.ORDERKEY JOIN "data/TPCH/SCALE-1/9/supplier.csv" AS s ON s.SUPPKEY = l.SUPPKEY JOIN "data/TPCH/SCALE-1/9/nation.csv" AS n ON n.NATIONKEY = s.NATIONKEY JOIN "data/TPCH/SCALE-1/9/region.csv" AS re ON re.REGIONKEY = n.REGIONKEY WHERE re.NAME = 'ASIA' ORDER BY l.REVENUE1 DESC'''),
        "constraints": Constraints(
            Constraint(Group("o.ORDERPRIORITY", "5-LOW"), (10, 5)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
        "k_list": [10],
    },
    {
        "name": "SF_Q5_TPCH_SF10-10",
        "dataset": "TPC-H-1000",
        "query_label": "data_size",
        "query": Query(['TPCH/SCALE-1/10/customer.csv'], label="1GB", verbatim='''SELECT c.*, o.*, l.*, s.*, n.*, re.* FROM "data/TPCH/SCALE-1/10/customer.csv" AS c JOIN "data/TPCH/SCALE-1/10/orders.csv" AS o ON o.CUSTKEY = c.CUSTKEY JOIN "data/TPCH/SCALE-1/10/lineitem.csv" AS l ON l.ORDERKEY = o.ORDERKEY JOIN "data/TPCH/SCALE-1/10/supplier.csv" AS s ON s.SUPPKEY = l.SUPPKEY JOIN "data/TPCH/SCALE-1/10/nation.csv" AS n ON n.NATIONKEY = s.NATIONKEY JOIN "data/TPCH/SCALE-1/10/region.csv" AS re ON re.REGIONKEY = n.REGIONKEY WHERE re.NAME = 'ASIA' ORDER BY l.REVENUE1 DESC'''),
        "constraints": Constraints(
            Constraint(Group("o.ORDERPRIORITY", "5-LOW"), (10, 5)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
        "k_list": [10],
    },
    # {
    #     "name": "SF_Q2-4-6-1_TPCH_SF10",
    #     "dataset": "TPCH_SF-10",
    #     "query": Query('TPCH/SCALE-10/lineitem.csv'). \
    #         where(
    #         Condition('SHIPDATE', '>=', 757382400),
    #         Condition('SHIPDATE', '<', 788918400),
    #         Condition('DISCOUNT', '>=', 0.05),
    #         Condition('DISCOUNT', '<=', 0.07),
    #         Condition('QUANTITY', '<', 20),
    #     ).order_by("REVENUE1", is_desc=True),
    #     "constraints": Constraints(
    #         Constraint(Group("LINESTATUS", 'O'), (3, 1)),
    #         Constraint(Group("SHIPMODE", 'MAIL'), (10, 1)),
    #         Constraint(Group("RETURNFLAG", 'R'), (4, 1)),
    #     ),
    #     "only_lower_bound_constraints": True,
    #     "max_deviations": [0.5],
    #     "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
    #     "k_list": [10],
    # },
    # {
    #     "name": "SF_Q2-4-6-1_TPCH_SF30",
    #     "dataset": "TPCH_SF-30",
    #     "query": Query('TPCH/SCALE-30/lineitem.csv'). \
    #         where(
    #         Condition('SHIPDATE', '>=', 757382400),
    #         Condition('SHIPDATE', '<', 788918400),
    #         Condition('DISCOUNT', '>=', 0.05),
    #         Condition('DISCOUNT', '<=', 0.07),
    #         Condition('QUANTITY', '<', 20),
    #     ).order_by("REVENUE1", is_desc=True),
    #     "constraints": Constraints(
    #         Constraint(Group("LINESTATUS", 'O'), (3, 1)),
    #         Constraint(Group("SHIPMODE", 'MAIL'), (10, 1)),
    #         Constraint(Group("RETURNFLAG", 'R'), (4, 1)),
    #     ),
    #     "only_lower_bound_constraints": True,
    #     "max_deviations": [0.5],
    #     "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
    #     "k_list": [10],
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
                        k_list=experiment['k_list']
                        )
        exprs.append(ex)

    runner = ExperimentsRunner(exprs, Path("experiments", 'SF', 'Q5'), iterations=5)
    runner.run()
