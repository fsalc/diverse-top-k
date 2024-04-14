from pathlib import Path

from ranking_refinements.fair import RefinementMethod
from ranking_refinements.experiments import Constraints, Constraint, Group, UsefulMethod, Query, Condition, Experiment, \
    ExperimentsRunner
import duckdb as d

d.sql(f"PRAGMA memory_limit='25GB';")
d.sql(f"PRAGMA threads=1;")

EXPERIMENTS = [
    {
        "name": "NumberOfConstraints_Ken_Law",
        "dataset": "law_students",
        "query": Query('law_students.csv'). \
            where(
            Condition('region_first', '=', 'GL'),
            Condition('UGPA', '>=', 3.5),
            Condition('UGPA', '<=', 4.0),
        ).order_by("LSAT", is_desc=True),
        "constraints": [
            Constraints(
                Constraint(Group("sex", 1), (3, 1)),
                label=1
            ),
            Constraints(
                Constraint(Group("sex", 1), (3, 1)),
                Constraint(Group("sex", 2), (3, 1)),
                label=2
            ),
            Constraints(
                Constraint(Group("sex", 1), (3, 1)),
                Constraint(Group("sex", 2), (3, 1)),
                Constraint(Group("race", "Black"), (5, 1)),
                label=3
            ),
            Constraints(
                Constraint(Group("sex", 1), (3, 1)),
                Constraint(Group("sex", 2), (3, 1)),
                Constraint(Group("race", "Black"), (5, 1)),
                Constraint(Group("race", "White"), (5, 1)),
                label=4
            ),
            Constraints(
                Constraint(Group("sex", 1), (3, 1)),
                Constraint(Group("sex", 2), (3, 1)),
                Constraint(Group("race", "Black"), (5, 1)),
                Constraint(Group("race", "White"), (5, 1)),
                Constraint(Group("race", "Asian"), (5, 1)),
                label=5
            )
        ],
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE],
        "algorithms": [RefinementMethod.MILP_OPT],
        "k_list": [10],
    },
    {
        "name": "NumberOfConstraints_Ken_Astronauts",
        "dataset": "astronauts",
        "query": Query('astronauts.csv'). \
            where(
            Condition('Graduate Major', '=', 'Physics'),
            Condition('Space Walks', '>=', 1),
            Condition('Space Walks', '<=', 3),
        ).order_by("Space Flight (hr)", is_desc=True),
        "constraints": [
            Constraints(
                Constraint(Group("Gender", "Female"), (3, 1)),
                label=1
            ),
            Constraints(
                Constraint(Group("Gender", "Female"), (3, 1)),
                Constraint(Group("Gender", "Male"), (3, 1)),
                label=2
            ),
            Constraints(
                Constraint(Group("Gender", "Female"), (3, 1)),
                Constraint(Group("Gender", "Male"), (3, 1)),
                Constraint(Group("Status", "Active"), (5, 1)),
                label=3
            ),
            Constraints(
                Constraint(Group("Gender", "Female"), (3, 1)),
                Constraint(Group("Gender", "Male"), (3, 1)),
                Constraint(Group("Status", "Active"), (5, 1)),
                Constraint(Group("Status", "Management"), (5, 1)),
                label=4
            ),
            Constraints(
                Constraint(Group("Gender", "Female"), (3, 1)),
                Constraint(Group("Gender", "Male"), (3, 1)),
                Constraint(Group("Status", "Active"), (5, 1)),
                Constraint(Group("Status", "Management"), (5, 1)),
                Constraint(Group("Status", "Retired"), (5, 1)),
                label=5
            ),
        ],
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE],
        "algorithms": [RefinementMethod.MILP_OPT],
        "k_list": [10],
    },
    {
        "name": "NumberOfConstraints_Ken_MEPS",
        "dataset": "MEPS",
        "query": Query('meps.csv'). \
            where(
            Condition('AGE16X', '>=', 25),
            Condition('FAMS1231', '>=', 4),
        ).order_by("rank", is_desc=True),

        "constraints": [
            Constraints(
                Constraint(Group("SEX", 1), (3, 1)),
                label=1
            ),
            Constraints(
                Constraint(Group("SEX", 1), (3, 1)),
                Constraint(Group("SEX", 2), (3, 1)),
                label=2
            ),
            Constraints(
                Constraint(Group("SEX", 1), (3, 1)),
                Constraint(Group("SEX", 2), (3, 1)),
                Constraint(Group("RACEV1X", 4), (5, 1)),
                label=3
            ),
            Constraints(
                Constraint(Group("SEX", 1), (3, 1)),
                Constraint(Group("SEX", 2), (3, 1)),
                Constraint(Group("RACEV1X", 4), (5, 1)),
                Constraint(Group("RACEV1X", 2), (5, 1)),
                label=4
            ),
            Constraints(
                Constraint(Group("SEX", 1), (3, 1)),
                Constraint(Group("SEX", 2), (3, 1)),
                Constraint(Group("RACEV1X", 4), (5, 1)),
                Constraint(Group("RACEV1X", 2), (5, 1)),
                Constraint(Group("RACEV1X", 1), (5, 1)),
                label=5
            ),
        ],
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE],
        "algorithms": [RefinementMethod.MILP_OPT],
        "k_list": [10],
    },
    {
        "name": "NumberOfConstraints_Ken_TPCH",
        "dataset": "TPC-H",
        "query": Query(['TPCH/SCALE-1/10/customer.csv'], verbatim='''SELECT c.*, o.*, l.*, s.*, n.*, re.* FROM "data/TPCH/SCALE-1/10/customer.csv" AS c JOIN "data/TPCH/SCALE-1/10/orders.csv" AS o ON o.CUSTKEY = c.CUSTKEY JOIN "data/TPCH/SCALE-1/10/lineitem.csv" AS l ON l.ORDERKEY = o.ORDERKEY JOIN "data/TPCH/SCALE-1/10/supplier.csv" AS s ON s.SUPPKEY = l.SUPPKEY JOIN "data/TPCH/SCALE-1/10/nation.csv" AS n ON n.NATIONKEY = s.NATIONKEY JOIN "data/TPCH/SCALE-1/10/region.csv" AS re ON re.REGIONKEY = n.REGIONKEY WHERE re.NAME = 'ASIA' ORDER BY l.REVENUE1 DESC'''),
        "constraints": [
            Constraints(
                Constraint(Group("o.ORDERPRIORITY", "5-LOW"), (10, 5)),
                label=1
            ),
            Constraints(
                Constraint(Group("o.ORDERPRIORITY", "5-LOW"), (10, 5)),
                Constraint(Group("o.ORDERPRIORITY", "3-MEDIUM"), (10, 2)),
                label=2
            ),
            Constraints(
                Constraint(Group("o.ORDERPRIORITY", "5-LOW"), (10, 5)),
                Constraint(Group("o.ORDERPRIORITY", "3-MEDIUM"), (10, 2)),
                Constraint(Group("c.MKTSEGMENT", "AUTOMOBILE"), (10, 2)),
                label=3
            ),
            Constraints(
                Constraint(Group("o.ORDERPRIORITY", "5-LOW"), (10, 5)),
                Constraint(Group("o.ORDERPRIORITY", "3-MEDIUM"), (10, 2)),
                Constraint(Group("c.MKTSEGMENT", "AUTOMOBILE"), (10, 2)),
                Constraint(Group("c.MKTSEGMENT", "BUILDING"), (10, 2)),
                label=4
            ),
            Constraints(
                Constraint(Group("o.ORDERPRIORITY", "5-LOW"), (10, 5)),
                Constraint(Group("o.ORDERPRIORITY", "3-MEDIUM"), (10, 2)),
                Constraint(Group("c.MKTSEGMENT", "AUTOMOBILE"), (10, 2)),
                Constraint(Group("c.MKTSEGMENT", "BUILDING"), (10, 2)),
                Constraint(Group("c.MKTSEGMENT", "MACHINERY"), (10, 2)),
                label=5
            ),
        ],
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE],
        "algorithms": [RefinementMethod.MILP_OPT],
        "k_list": [10]
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
                        k_list=experiment['k_list'],
                        constraints_label="number_of_constraints"
                        )
        exprs.append(ex)

    runner = ExperimentsRunner(exprs, Path("experiments", 'number_of_constraints', 'kendall'),
                               [("total_duration[sec]", "algorithm"), ("deviation", "algorithm")],
                               iterations=10)
    runner.run()
