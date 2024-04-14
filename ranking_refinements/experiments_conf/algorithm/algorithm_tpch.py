from pathlib import Path

from ranking_refinements.fair import RefinementMethod
from ranking_refinements.experiments import Constraints, Constraint, Group, UsefulMethod, Query, Condition, Experiment, ExperimentsRunner

EXPERIMENTS = [
    {
        "name": "ALG_CombUseful_TPCH",
        "dataset": "TPCH-H",
        "query": Query(['TPCH/SCALE-1/10/customer.csv'], verbatim='''SELECT c.*, o.*, l.*, s.*, n.*, re.* FROM "data/TPCH/SCALE-1/10/customer.csv" AS c JOIN "data/TPCH/SCALE-1/10/orders.csv" AS o ON o.CUSTKEY = c.CUSTKEY JOIN "data/TPCH/SCALE-1/10/lineitem.csv" AS l ON l.ORDERKEY = o.ORDERKEY JOIN "data/TPCH/SCALE-1/10/supplier.csv" AS s ON s.SUPPKEY = l.SUPPKEY JOIN "data/TPCH/SCALE-1/10/nation.csv" AS n ON n.NATIONKEY = s.NATIONKEY JOIN "data/TPCH/SCALE-1/10/region.csv" AS re ON re.REGIONKEY = n.REGIONKEY WHERE re.NAME = 'ASIA' ORDER BY l.REVENUE1 DESC'''),
        "constraints": Constraints(
            Constraint(Group("o.ORDERPRIORITY", "5-LOW"), (10, 5)),
        ),
        "only_lower_bound_constraints": True,
        "max_deviations": [0.5],
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL],
        "algorithms": [RefinementMethod.MILP_OPT, RefinementMethod.BRUTE_PROV, RefinementMethod.BRUTE],
        "k_list": [10],
        "comparison_criteria": [("runtime [sec]", "algorithm"), ("deviation", "algorithm")],
        "iterations": 5
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

    runner = ExperimentsRunner(exprs, Path("experiments", 'algorithm', 'tpch'),
                               [("duration[sec]", "algorithm"), ("deviation", "algorithm")],
                               iterations=5)
    runner.run()
