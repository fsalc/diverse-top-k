from pathlib import Path

from ranking_refinements.fair import RefinementMethod
from ranking_refinements.experiments import Constraints, Constraint, Group, UsefulMethod, Query, Condition, Experiment, ExperimentsRunner

EXPERIMENTS = [
    {
        "name": "ALG_CombUseful_Astronauts",
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
        "useful_methods": [UsefulMethod.KENDALL_DISTANCE, UsefulMethod.QUERY_DISTANCE,
                           UsefulMethod.MAX_ORIGINAL],
        "algorithms": [RefinementMethod.MILP_OPT, RefinementMethod.MILP, RefinementMethod.BRUTE_PROV, RefinementMethod.BRUTE],
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

    runner = ExperimentsRunner(exprs, Path("experiments", 'algorithm', 'astronauts'),
                               [("duration[sec]", "algorithm"), ("deviation", "algorithm")],
                               iterations=5)
    runner.run()
