import os.path
import pathlib
from timeit import default_timer as timer
from pathlib import Path
from typing import Union, List

from multiprocessing import Process

from ranking_refinements.fair import Ranking, Constraints, Constraint, Group, UsefulMethod, RefinementMethod
from ranking_refinements.query import Query, Condition

import numpy as np
from copy import deepcopy

import csv

from ranking_refinements.utils import timeout


class Experiment:

    def __init__(self,
                 name: str,
                 dataset: str,
                 query: Union[Query, List[Query]],
                 cons: Union[Constraints, List[Constraints]],
                 max_deviations=np.arange(0.0, 1.1, 0.1),
                 useful_methods=(
                         UsefulMethod.QUERY_DISTANCE, UsefulMethod.JACCARD_DISTANCE, UsefulMethod.KENDALL_DISTANCE),
                 k_list: List[int] = None,
                 algorithms: List[RefinementMethod] = None,
                 only_lower_bound_constraints: bool = False,
                 constraints_label: str = None,
                 query_label: str = None,
                 ):

        self.name = name
        self.dataset = dataset
        self.query = query if isinstance(query, list) else [query]
        # self.ranking = Ranking(query.build())
        self.constraints = cons if isinstance(cons, list) else [cons]

        ###
        _cons: List[Constraint] = []
        for c in self.constraints:
            _cons += c.constraints
        self.merged_constraints = Constraints(*_cons)
        ###
        self.only_lower_bound_constraints = only_lower_bound_constraints
        self.max_deviations = max_deviations
        self.useful_methods = useful_methods
        self.k_list = k_list
        self.algorithms = algorithms or [RefinementMethod.MILP_OPT]
        self.constraints_label = constraints_label
        self.query_label = query_label


class ExperimentsRunner:

    def __init__(self, experiments: List[Experiment], output_dir=Path("experiments", 'experiment_pkg'),
                 comparison_criteria=None, name='experiment_pkg', iterations: int = 1):
        self.experiments = experiments
        self.output_dir = output_dir
        self.comparison_criteria = comparison_criteria
        self.name = name
        self.iterations = iterations

    def run(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        statistics_out_files = []
        datasets = []

        for expr in self.experiments:
            statistics_output_file = Path(self.output_dir, expr.name, "statistics.csv")
            statistics_out_files.append(statistics_output_file)
            datasets.append(expr.dataset)
            result_output_file = Path(self.output_dir, expr.name, "result.txt")
            if not os.path.exists(Path(self.output_dir, expr.name)):
                os.makedirs(Path(self.output_dir, expr.name))

            with open(statistics_output_file, 'w', newline='') as output:
                writer = csv.writer(output)
                writer.writerow(
                    ['no', 'max_deviation', 'K', 'useful_method', 'deviation', 'algorithm'] + [f"COUNT({c.group})" for c in
                                                                                               expr.merged_constraints] +
                    [expr.constraints_label, expr.query_label] +
                    ['setup_duration[sec]', 'solver_duration[sec]', 'total_duration[sec]'])
            with open(result_output_file, 'w'):
                pass
            i = 1

            for algorithm in expr.algorithms:
                for max_deviation in expr.max_deviations:
                    for useful_method in expr.useful_methods:
                        for k in expr.k_list:
                            for query in expr.query:
                                for constraints_set in expr.constraints:
                                    cur_constraints = deepcopy(constraints_set)
                                    factors = [[card[1] / card[0] for card in c.cardinalities] for c in cur_constraints]
                                    for i in range(len(cur_constraints)):
                                        c = cur_constraints[i]
                                        c.cardinalities = [(k, k * factors[i][j]) for j in range(len(c.cardinalities))]
                                    cur_constraints = Constraints(*cur_constraints.constraints)

                                    for iter in range(self.iterations):
                                        constraints = cur_constraints
                                        is_lower_bound_only = constraints.label != 'Combined' and \
                                                      constraints.label != 'UpperBound' and \
                                                      expr.only_lower_bound_constraints
                                        ####
                                        @timeout(3600)
                                        def refine():
                                            return Ranking(query.build()).refine(constraints,
                                                                                      max_deviation=max_deviation,
                                                                                      useful_method=useful_method,
                                                                                      only_lower_bound_card_constraints=is_lower_bound_only,
                                                                                      method=algorithm)

                                        try:
                                            refinement, times = refine()
                                        except (TimeoutError, MemoryError):
                                            refinement, times = None, (0, 0, 3600)
                                        setup_duration = times[1] - times[0]
                                        solver_duration = times[2] - times[1]
                                        total_duration = times[2] - times[0]

                                        ####

                                        if refinement:
                                            q = deepcopy(query).clean_conditions()
                                            tuples = q.where(refinement.conditions).limit(k).run()

                                        ### all counts
                                        all_counts = [] if refinement else [-1 for c in expr.merged_constraints]
                                        if refinement:
                                            for constraint in expr.merged_constraints:
                                                all_counts.append(
                                                    len([t for t in tuples[constraint.group.attr if '.' not in constraint.group.attr else constraint.group.attr.split(".")[-1]] if
                                                         t == constraint.group.val]))

                                        # only current constraints counts
                                        counts = [] if refinement else [-1 for c in constraints]
                                        if refinement:
                                            for constraint in constraints:
                                                counts.append(
                                                    len([t for t in tuples[constraint.group.attr if '.' not in constraint.group.attr else constraint.group.attr.split(".")[-1]] if t == constraint.group.val]))

                                        deviation = 0
                                        constraint_weight = 1 / len(counts)
                                        for i in range(len(counts)):
                                            deviation += max(constraints[i].cardinalities[0][1] - counts[i], 0) / \
                                                         constraints[i].cardinalities[0][1] * constraint_weight

                                        with open(result_output_file, 'a') as output:
                                            output.write(f'{refinement}\n' if refinement else 'Infeasible\n')
                                        with open(statistics_output_file, 'a', newline='') as output:
                                            writer = csv.writer(output)
                                            writer.writerow(
                                                [iter, round(max_deviation, 2), k, useful_method.name, deviation, algorithm] +
                                                all_counts + [constraints_set.label, query.label] +
                                                [setup_duration, solver_duration, total_duration]
                                            )

                                        i += 1

        # plot_figure(statistics_out_files, datasets, self.comparison_criteria, self.output_dir)


if __name__ == '__main__':
    cons = Constraints(
        Constraint(Group("Gender", "Female"), (10, 5)),
        Constraint(Group("Gender", "Male"), (10, 5)),
    )

    query = Query('astronauts.csv'). \
        where(
        Condition('Graduate Major', '=', 'Physics'),
        Condition('Space Walks', '>=', 1),
        Condition('Space Walks', '<=', 3),
    ).order_by("Space Flight (hr)", is_desc=True)

    experiments = [
        # {
        #     "name": "DifferentWeightsWithResultDistance",
        #     "query": query,
        #     "constraints": cons,
        #     "max_deviations": [0.7],
        #     "useful_weights": np.arange(0.0, 1.1, 0.1),
        #     "useful_methods": [UsefulMethod.RESULT_DISTANCE],
        #     "k_list": [10],
        #     "comparison_criteria": [("runtime [sec]", "useful_weight"), ("fairness_score", "useful_weight")],
        #     "iterations": 10
        # },
        # {
        #     "name": "DifferentUsefulMethodsSameWeights",
        #     "query": query,
        #     "constraints": cons,
        #     "max_deviations": [0.7],
        #     "useful_weights": [0.5],
        #     "useful_methods": [UsefulMethod.RESULT_DISTANCE, UsefulMethod.SIZE, UsefulMethod.QUERY_DISTANCE],
        #     "k_list": [10],
        #     "comparison_criteria": [("runtime [sec]", "useful_method"), ("fairness_score", "useful_method")],
        #     "iterations": 10
        # },
        # {
        #     "name": "DifferentMaxDeviationsSameUsefulWeightsAndMethods",
        #     "query": query,
        #     "constraints": Constraints(
        #         Constraint(Group("Gender", "Female"), (30, 26))
        #     ),
        #     "max_deviations": np.arange(0.0, 1.1, 0.1),
        #     "useful_weights": [0.5],
        #     "useful_methods": [UsefulMethod.RESULT_DISTANCE],
        #     "k_list": [30],
        #     "comparison_criteria": [("runtime [sec]", "max_deviation"), ("fairness_score", "max_deviation")],
        #     "iterations": 10
        # },
        # {
        #     "name": "DifferentK",
        #     "dataset": "astronauts",
        #     "query": query,
        #     "constraints": Constraints(
        #         Constraint(Group("Gender", "Female"), (10, 5))
        #     ),
        #     "only_lower_bound_constraint": True,
        #     "max_deviations": [0.0],
        #     "useful_methods": [UsefulMethod.RESULT_DISTANCE],
        #     "k_list": range(10, 21, 10),
        #     "comparison_criteria": [("runtime [sec]", "K"), ("deviation", "K")],
        #     "iterations": 10
        # },
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
            "k_list": range(10, 101, 10),
            "comparison_criteria": [("runtime [sec]", "K"), ("deviation", "K")],
            "iterations": 10
        },
    ]

    for experiment in experiments:
        ex = Experiment(experiment['name'],
                        experiment['dataset'],
                        experiment['query'],
                        experiment['constraints'],
                        only_lower_bound_constraints=experiment['only_lower_bound_constraints'],
                        max_deviations=experiment['max_deviations'],
                        useful_methods=experiment['useful_methods'],
                        k_list=experiment['k_list']
                        )
        runner = ExperimentsRunner([ex], Path("experiments", '1'), [("runtime [sec]", "K"), ("deviation", "K")])

        runner.run()
