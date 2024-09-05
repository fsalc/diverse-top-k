from pathlib import Path

import numpy as np

from ranking_refinements.fair import RefinementMethod
from ranking_refinements.experiments import Constraints, Constraint, Group, UsefulMethod, Query, Condition, Experiment, ExperimentsRunner

EXPERIMENTS = [{
    "name": "ALG_CombUseful_Law",
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
    "useful_methods": [UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL, UsefulMethod.KENDALL_DISTANCE],
    "k_list": [10],
    "algorithms": [RefinementMethod.MILP_OPT, RefinementMethod.MILP, RefinementMethod.BRUTE, RefinementMethod.BRUTE_PROV],
    "comparison_criteria": [("runtime [sec]", "algorithm"), ("deviation", "algorithm")],
    "iterations": 5
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

    runner = ExperimentsRunner(exprs, Path("experiments", 'algorithm', 'law'),
                               [("duration[sec]", "algorithm"), ("deviation", "algorithm")],
                               iterations=5)
    runner.run()
