import os.path
from collections import defaultdict
from pathlib import Path
from enum import Enum

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ranking_refinements.fair import RefinementMethod, UsefulMethod
import seaborn as sns
import numpy as np
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import PercentFormatter
import os

import subprocess

# matplotlib.use('pgf')

plt.rc('text')
plt.rc('font', family='serif')
plt.rc('text', usetex=False)
plt.rc('pgf',rcfonts=False)
# sns.set_palette("Paired")
# sns.set_palette("deep")
sns.set_context("poster")
sns.set_style("whitegrid")
# sns.palplot(sns.color_palette("deep", 10))
# sns.palplot(sns.color_palette("Paired", 9))
plt.tight_layout()

label = ["Naive", "Optimized"]
LINE_WIDTH = 5
MARKER_SIZE = 12
f_size = (14, 10)

# f_size = (14, 7)
all_plot_f_size = (40, 8)

FONT_SIZE = 36
plt.rc('font', size=FONT_SIZE)  # controls default text sizes
plt.rc('axes', titlesize=FONT_SIZE)  # fontsize of the axes title
plt.rc('axes', labelsize=FONT_SIZE)  # fontsize of the x and y labels
plt.rc('xtick', labelsize=FONT_SIZE)  # fontsize of the tick labels
plt.rc('ytick', labelsize=FONT_SIZE)  # fontsize of the tick labels
plt.rc('legend', fontsize=FONT_SIZE)  # legend fontsize
plt.rc('figure', titlesize=42)  # fontsize of the figure title
from matplotlib import rcParams

rcParams['axes.titlepad'] = 0

EXPERIMENT_PATH = Path('.', 'experiments')
OUTPUT_DIR = Path('./figures/')
BAR_WIDTH = 0.2

K_LIST = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
MAX_DEVIATION_LIST = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]


class Stage(Enum):
    SETUP = 0
    SOLVER = 1
    TOTAL = 3


# COLORS = {
#     UsefulMethod.MAX_ORIGINAL: {Stage.SETUP: 'greenyellow', Stage.SOLVER: 'olivedrab', Stage.TOTAL: 'olivedrab'},
#     UsefulMethod.KENDALL_DISTANCE: {Stage.SETUP: 'lightsteelblue', Stage.SOLVER: 'cornflowerblue',
#                                     Stage.TOTAL: 'cornflowerblue'},
#     UsefulMethod.JACCARD_DISTANCE: {Stage.SETUP: 'darkkhaki', Stage.SOLVER: 'gold', Stage.TOTAL: 'gold'},
#     UsefulMethod.QUERY_DISTANCE: {Stage.SETUP: 'violet', Stage.SOLVER: 'darkviolet', Stage.TOTAL: 'darkviolet'},
#     'Astr': {Stage.SETUP: 'orchid', Stage.SOLVER: 'purple', Stage.TOTAL: 'purple'},
#     'Law': {Stage.SETUP: 'wheat', Stage.SOLVER: 'orange', Stage.TOTAL: 'orange'},
#     'MEPS': {Stage.SETUP: 'lightskyblue', Stage.SOLVER: 'steelblue', Stage.TOTAL: 'steelblue'},
# }

COLORS = {
    UsefulMethod.MAX_ORIGINAL: 'C2',
    UsefulMethod.KENDALL_DISTANCE: 'C0',
    UsefulMethod.JACCARD_DISTANCE: 'C2',
    UsefulMethod.QUERY_DISTANCE: 'C3',
    'Astr': {Stage.SETUP: 'xkcd:lime', Stage.SOLVER: 'lime', Stage.TOTAL: 'lime'},
    'Law': {Stage.SETUP: 'xkcd:orange', Stage.SOLVER: 'orange', Stage.TOTAL: 'orange'},
    'MEPS': {Stage.SETUP: 'xkcd:violet', Stage.SOLVER: 'violet', Stage.TOTAL: 'violet'},
    'TPC-H': 'xkcd:light rose'
}
LINE_STYLES = ['o-', 's--', '^:', '-.p']

LINE_STYLES_BY_STAGE = {
    Stage.SETUP: 'o-',
    Stage.TOTAL: '^:',
    Stage.SOLVER: 's--'
}

LINE_STYLES_BY_COLOR_INDEX_AND_STAGE = {
    UsefulMethod.JACCARD_DISTANCE: {
        Stage.SETUP: 'o--',
        Stage.TOTAL: 'o-'
    },
    UsefulMethod.QUERY_DISTANCE: {
        Stage.SETUP: 's--',
        Stage.TOTAL: 's-'
    },
    UsefulMethod.KENDALL_DISTANCE: {
        Stage.SETUP: 'p--',
        Stage.TOTAL: 'p-'
    },
    UsefulMethod.MAX_ORIGINAL: {
        Stage.SETUP: 'o--',
        Stage.TOTAL: 'o-'
    },
}

HATCH_BY_STAGE = {
    Stage.SETUP: 'oo',
    Stage.TOTAL: '\\\\',
    Stage.SOLVER: 'xx'
}
HATCH_BY_COLOR_INDEX_AND_STAGE = {
    UsefulMethod.JACCARD_DISTANCE: {
        Stage.SETUP: 'OO',
        Stage.SOLVER: '\\\\'
    },
    UsefulMethod.MAX_ORIGINAL: {
        Stage.SETUP: 'OO',
        Stage.SOLVER: '\\\\'
    },
    UsefulMethod.QUERY_DISTANCE: {
        Stage.SETUP: 'xx',
        Stage.SOLVER: '//'
    },
    UsefulMethod.KENDALL_DISTANCE: {
        Stage.SETUP: '..',
        Stage.SOLVER: '**'
    },
    'TPC-H': {
        Stage.SETUP: '..',
        Stage.SOLVER: '**'
    },
    'Astr': {
        Stage.SETUP: '..',
        Stage.SOLVER: '**'
    }
}

PLOT_ORDER = ['JAC', 'QD', 'KEN', 'MAX_ORIGINAL', 'QUERY_DISTANCE', 'KENDALL_DISTANCE']


def plot_bar(index, y, hatch=None, color=None, label=None, width=BAR_WIDTH, bottom=None, annotations=None, ax=None,
             gap=0.0):
    ax = ax or plt.gca()
    plt.bar(index + gap, y, width, color=color, label=label, bottom=bottom, hatch=hatch)
    # if annotations is not None:
    #     # print(y+bottom)
    #     # highs = [y[i] + bottom[i] for i in range(len(y))] if bottom is not None else y
    #     highs = y + bottom
    #     for i, j, annotation in zip(index, highs, annotations):
    #         ax.annotate('({:,.2})'.format(annotation), xy=(i + gap - (0.35 * width), j), fontsize=18)


def plot_line(index, y, linestyle=None, color=None, label=None, annotations=None, ax=None):
    ax = ax or plt.gca()
    plt.plot(index, y, linestyle, color=color, label=label, linewidth=LINE_WIDTH, markersize=MARKER_SIZE)
    # gap = 0.1 if max(y) - min(y) > 1 else 0.01 if max(y) - min(y) > 0.2 else 0.001
    # if annotations is not None:
    #     for i, j, annotation in zip(index, y, annotations):
    #         if annotation == -1: 
    #             ax.annotate('(*)'.format(annotation), xy=(i, j + gap), fontsize=18)
    #         else:
    #             ax.annotate('({:,.2})'.format(annotation), xy=(i, j + gap), fontsize=18)


def plot_bar_duration_graph(index, y_setup, y_solver, color_index, legend_prefix, width=BAR_WIDTH, hatch=None,
                            annotations=None, ax=None, gap_number=0, is_split=True):
    # Naive doesn't have setup, so combine and plot here if is_split is False
    if not is_split:
            plot_bar(index, y_setup+y_solver, hatch or HATCH_BY_COLOR_INDEX_AND_STAGE[color_index][Stage.SOLVER], COLORS[color_index],
             label=f'{legend_prefix}-Solver',
             width=width, annotations=annotations, ax=ax, gap=gap_number * width)
    else:
        plot_bar(index, y_setup, hatch or HATCH_BY_COLOR_INDEX_AND_STAGE[color_index][Stage.SETUP], COLORS[color_index], label=f'{legend_prefix}-Setup',
                width=width, gap=gap_number * width)
        plot_bar(index, y_solver, hatch or HATCH_BY_COLOR_INDEX_AND_STAGE[color_index][Stage.SOLVER], COLORS[color_index], bottom=y_setup,
                label=f'{legend_prefix}-Solver',
                width=width, annotations=annotations, ax=ax, gap=gap_number * width)


def plot_lines_duration_graph(index, y_setup, y_total, color_index, legend_prefix, linestyle=None, annotations=None,
                              ax=None):
    plot_line(index, y_setup, linestyle or LINE_STYLES_BY_COLOR_INDEX_AND_STAGE[color_index][Stage.SETUP], COLORS[color_index],
              label=f'{legend_prefix}-Setup')
    plot_line(index, y_total, linestyle or LINE_STYLES_BY_COLOR_INDEX_AND_STAGE[color_index][Stage.TOTAL], COLORS[color_index],
              label=f'{legend_prefix}-Total', annotations=annotations, ax=ax)


def plot_features(index, x_values, x_label, y_label, title, legend_loc='best', should_show_legend=True):
    if type(x_values) is not list and x_values.get('LowerBound'): x_values['LowerBound'] = 'Lower Bound'
    plt.xticks(index + BAR_WIDTH, x_values, fontweight='light', fontsize=36)

    plt.xlabel(x_label)
    plt.ylabel(y_label)

    plt.autoscale()
    if should_show_legend:
        plt.legend(loc='lower center', prop={'size': 24}, handlelength=3, handleheight=0.2, ncol=3, bbox_to_anchor=(0.5, 1), frameon=False, columnspacing=0.5)
    plt.grid(True)

    # TODO: turn on automatically for relevant graphs
    # ax = plt.gca()
    # for i, l in enumerate(ax.xaxis.get_ticklabels(which='both')):
    #     if i % 2 == 1:
    #         l.set_visible(False)

    # plt.title(title)


def _get_index(x):
    return np.arange(len(x))


def plot_durations_graphs(x, y_setup, y_solver, y_total, deviations,
                          color_index, legend_prefix,
                          x_label, title, output_dir, output_name, y_label='duration[sec]'):
    index = _get_index(x)
    plot_bar_duration_graph(index, y_setup, y_solver, color_index, legend_prefix)
    plot_features(index, x, x_label, y_label, title)
    plt.savefig(Path(output_dir, f'{output_name}__{y_label}_by_{x_label}__bar.pdf', bbox_inches='tight', format="pdf"), bbox_inches='tight')
    plt.clf()
    plt.close()
    # plt.show()

    plot_lines_duration_graph(index, y_setup, y_total, color_index, legend_prefix, annotations=deviations, ax=ax)
    plot_features(index, x, x_label, y_label, title)
    plt.savefig(Path(output_dir, f'{output_name}__{y_label}_by_{x_label}__lines.pdf'), bbox_inches='tight', format="pdf")
    plt.clf()
    plt.close()
    # plt.show()


def get_axises_from_df(df, x_axis):
    y_total = df.groupby(x_axis, sort=False)['total_duration[sec]'].mean()
    y_setup = df.groupby(x_axis, sort=False)['setup_duration[sec]'].mean()
    y_solver = df.groupby(x_axis, sort=False)['solver_duration[sec]'].mean()
    deviations = df.groupby(x_axis, sort=False)['deviation'].mean()
    x = df.groupby(x_axis, sort=False)[x_axis].first()
    return x, y_setup, y_solver, y_total, deviations


def plot_duration_from_df(df, x_axis, color_index, legend_prefix,
                          graph_title, output_name, output_dir=OUTPUT_DIR):
    x, y_setup, y_solver, y_total, deviations = get_axises_from_df(df, x_axis)
    plot_durations_graphs(x, y_setup, y_solver, y_total, deviations, color_index, legend_prefix, x_axis,
                          graph_title, output_dir, output_name)


DF_K_MO_ASTR = pd.read_csv(Path('.', 'experiments', 'K', 'max_original', 'K_MO_Astronauts', 'statistics.csv'))
DF_MaxDev_MO_ASTR = pd.read_csv(
    Path('.', 'experiments', 'max_dev', 'max_original', 'MaxDev_MO_Astronauts', 'statistics.csv'))

ALGORITHM_COMPARISON_STATISTICS = [
    # ('Law', Path('.', 'experiments', 'algorithm', 'law', 'ALG_CombUseful_Law', 'statistics.csv')),
    # ('MEPS', Path('.', 'experiments', 'algorithm', 'meps', 'ALG_CombUseful_MEPS', 'statistics.csv')),
    ('Astr', Path('.', 'experiments', 'algorithm', 'astronauts', 'ALG_CombUseful_Astronauts', 'statistics.csv')),
    ('Law', Path('.', 'experiments', 'algorithm', 'law', 'ALG_CombUseful_Law', 'statistics.csv')),
    ('MEPS', Path('.', 'experiments', 'algorithm', 'meps', 'ALG_CombUseful_MEPS', 'statistics.csv')),
    ('TPC-H', Path('.', 'experiments', 'algorithm', 'tpch', 'ALG_CombUseful_TPCH', 'statistics.csv')),
]

DATA_SIZE_COMPARISON_STATISTICS = [
    ('Astronauts', Path('.', 'experiments', 'SF', 'astronauts', 'statistics.csv'), 'KB'),
    ('Law', Path('.', 'experiments', 'SF', 'law', 'statistics.csv'), 'KB'),
    ('MEPS', Path('.', 'experiments', 'SF', 'meps', 'statistics.csv'), 'MB'),
    ('TPC-H', Path('.', 'experiments', 'SF', 'Q5', 'statistics.csv'), 'MB'),
]

LINEAGE_CLASSES_COMPARISON_STATISTICS = [
    ('TPC-H', Path('.', 'experiments', 'lineage_classes', 'Q5', 'statistics.csv')),
    ('Astronauts', Path('.', 'experiments', 'lineage_classes', 'astronauts', 'statistics.csv')),
    ('Law', Path('.', 'experiments', 'lineage_classes', 'law', 'statistics.csv')),
]

STATISTICS = {
    'K': {
        'JAC': {
            'Astr': Path('.', 'experiments', 'K', 'max_original', 'K_MO_Astronauts', 'statistics.csv'),
            'Law': Path('.', 'experiments', 'K', 'max_original', 'K_MO_Law', 'statistics.csv'),
            'MEPS': Path('.', 'experiments', 'K', 'max_original', 'K_MO_MEPS', 'statistics.csv'),
            'TPC-H': Path('.', 'experiments', 'K', 'max_original', 'K_MO_TPCHQ5', 'statistics.csv'),
        },
        # 'JAC': {
        #     'Astr': Path('.', 'experiments', 'K', 'jaccard', 'K_JAC_Astronauts', 'statistics.csv'),
        #     'Law': Path('.', 'experiments', 'K', 'jaccard', 'K_JAC_Law', 'statistics.csv'),
        #     'MEPS': Path('.', 'experiments', 'K', 'jaccard', 'K_JAC_MEPS', 'statistics.csv'),
        # },
        'QD': {
            'Astr': Path('.', 'experiments', 'K', 'query_distance', 'K_QD_Astronauts', 'statistics.csv'),
            'Law': Path('.', 'experiments', 'K', 'query_distance', 'K_QD_Law', 'statistics.csv'),
            'MEPS': Path('.', 'experiments', 'K', 'query_distance', 'K_QD_MEPS', 'statistics.csv'),
            'TPC-H': Path('.', 'experiments', 'K', 'query_distance', 'K_QD_TPCHQ5', 'statistics.csv'),
        },
        'KEN': {
            'Astr': Path('.', 'experiments', 'K', 'kendall', 'K_Ken_Astronauts', 'statistics.csv'),
            'Law': Path('.', 'experiments', 'K', 'kendall', 'K_Ken_Law', 'statistics.csv'),
            'MEPS': Path('.', 'experiments', 'K', 'kendall', 'K_Ken_MEPS', 'statistics.csv'),
            'TPC-H': Path('.', 'experiments', 'K', 'kendall', 'K_Ken_TPCHQ5', 'statistics.csv'),
        }
    },
    'max_deviation': {
        'JAC': {
            'Astr': Path('.', 'experiments', 'max_dev', 'max_original', 'MaxDev_MO_Astronauts', 'statistics.csv'),
            'Law': Path('.', 'experiments', 'max_dev', 'max_original', 'MaxDev_MO_Law', 'statistics.csv'),
            'MEPS': Path('.', 'experiments', 'max_dev', 'max_original', 'MaxDev_MO_MEPS', 'statistics.csv'),
            'TPC-H': Path('.', 'experiments', 'max_dev', 'max_original', 'MaxDev_MO_TPCHQ5', 'statistics.csv'),
        },
        # 'JAC': {
        #     'Astr': Path('.', 'experiments', 'max_dev', 'jaccard', 'MaxDev_JAC_Astronauts', 'statistics.csv'),
        #     'Law': Path('.', 'experiments', 'max_dev', 'jaccard', 'MaxDev_JAC_Law', 'statistics.csv'),
        #     'MEPS': Path('.', 'experiments', 'max_dev', 'jaccard', 'MaxDev_JAC_MEPS', 'statistics.csv'),
        # },
        'QD': {
            'Astr': Path('.', 'experiments', 'max_dev', 'query_distance', 'MaxDev_QD_Astronauts', 'statistics.csv'),
            'Law': Path('.', 'experiments', 'max_dev', 'query_distance', 'MaxDev_QD_Law', 'statistics.csv'),
            'MEPS': Path('.', 'experiments', 'max_dev', 'query_distance', 'MaxDev_QD_MEPS', 'statistics.csv'),
            'TPC-H': Path('.', 'experiments', 'max_dev', 'query_distance', 'MaxDev_QD_TPCHQ5', 'statistics.csv'),
        },
        'KEN': {
            'Astr': Path('.', 'experiments', 'max_dev', 'kendall', 'MaxDev_KEN_Astronauts', 'statistics.csv'),
            'Law': Path('.', 'experiments', 'max_dev', 'kendall', 'MaxDev_KEN_Law', 'statistics.csv'),
            'MEPS': Path('.', 'experiments', 'max_dev', 'kendall', 'MaxDev_KEN_MEPS', 'statistics.csv'),
            'TPC-H': Path('.', 'experiments', 'max_dev', 'kendall', 'MaxDev_KEN_TPCHQ5', 'statistics.csv'),
        }
    },
    'number_of_constraints': {
        'JAC': {
            'Astr': Path('.', 'experiments', 'number_of_constraints', 'max_original',
                         'NumberOfConstraints_MO_Astronauts', 'statistics.csv'),
            'Law': Path('.', 'experiments', 'number_of_constraints', 'max_original', 'NumberOfConstraints_MO_Law',
                        'statistics.csv'),
            'MEPS': Path('.', 'experiments', 'number_of_constraints', 'max_original', 'NumberOfConstraints_MO_MEPS',
                         'statistics.csv'),
            'TPC-H': Path('.', 'experiments', 'number_of_constraints', 'max_original', 'NumberOfConstraints_MO_TPCH',
                         'statistics.csv'),
        },
        # 'JAC': {
        #     'Astr': Path('.', 'experiments', 'number_of_constraints', 'jaccard', 'NumberOfConstraints_JAC_Astronauts',
        #                  'statistics.csv'),
        #     'Law': Path('.', 'experiments', 'number_of_constraints', 'jaccard', 'NumberOfConstraints_JAC_Law',
        #                 'statistics.csv'),
        #     'MEPS': Path('.', 'experiments', 'number_of_constraints', 'jaccard', 'NumberOfConstraints_JAC_MEPS',
        #                  'statistics.csv'),
        # },
        'QD': {
            'Astr': Path('.', 'experiments', 'number_of_constraints', 'query_distance',
                         'NumberOfConstraints_QD_Astronauts', 'statistics.csv'),
            'Law': Path('.', 'experiments', 'number_of_constraints', 'query_distance', 'NumberOfConstraints_QD_Law',
                        'statistics.csv'),
            'MEPS': Path('.', 'experiments', 'number_of_constraints', 'query_distance', 'NumberOfConstraints_QD_MEPS',
                         'statistics.csv'),
            'TPC-H': Path('.', 'experiments', 'number_of_constraints', 'query_distance', 'NumberOfConstraints_QD_TPCH',
                         'statistics.csv'),
        },
        'KEN': {
            'Astr': Path('.', 'experiments', 'number_of_constraints', 'kendall', 'NumberOfConstraints_Ken_Astronauts',
                         'statistics.csv'),
            'Law': Path('.', 'experiments', 'number_of_constraints', 'kendall', 'NumberOfConstraints_Ken_Law',
                        'statistics.csv'),
            'MEPS': Path('.', 'experiments', 'number_of_constraints', 'kendall', 'NumberOfConstraints_Ken_MEPS',
                         'statistics.csv'),
            'TPC-H': Path('.', 'experiments', 'number_of_constraints', 'kendall', 'NumberOfConstraints_Ken_TPCH',
                         'statistics.csv'),
        }
    },
    'constraints_bounds': {
        'JAC': {
            'Astr': Path('.', 'experiments', 'constraints_bounds', 'max_original',
                         'ConstraintsBounds_MO_Astronauts', 'statistics.csv'),
            'Law': Path('.', 'experiments', 'constraints_bounds', 'max_original', 'ConstraintsBounds_MO_Law',
                        'statistics.csv'),
            'MEPS': Path('.', 'experiments', 'constraints_bounds', 'max_original', 'ConstraintsBounds_MO_MEPS',
                         'statistics.csv'),
            'TPC-H': Path('.', 'experiments', 'constraints_bounds', 'max_original', 'ConstraintsBounds_MO_TPCH',
                         'statistics.csv'),
        },
        # 'JAC': {
        #     'Astr': Path('.', 'experiments', 'constraints_bounds', 'jaccard', 'ConstraintsBounds_JAC_Astronauts',
        #                  'statistics.csv'),
        #     'Law': Path('.', 'experiments', 'constraints_bounds', 'jaccard', 'ConstraintsBounds_JAC_Law',
        #                 'statistics.csv'),
        #     'MEPS': Path('.', 'experiments', 'constraints_bounds', 'jaccard', 'ConstraintsBounds_JAC_MEPS',
        #                  'statistics.csv'),
        # },
        'QD': {
            'Astr': Path('.', 'experiments', 'constraints_bounds', 'query_distance',
                         'ConstraintsBounds_QD_Astronauts', 'statistics.csv'),
            'Law': Path('.', 'experiments', 'constraints_bounds', 'query_distance', 'ConstraintsBounds_QD_Law',
                        'statistics.csv'),
            'MEPS': Path('.', 'experiments', 'constraints_bounds', 'query_distance', 'ConstraintsBounds_QD_MEPS',
                         'statistics.csv'),
            'TPC-H': Path('.', 'experiments', 'constraints_bounds', 'query_distance', 'ConstraintsBounds_QD_TPCH',
                         'statistics.csv'),
        },
        'KEN': {
            'Astr': Path('.', 'experiments', 'constraints_bounds', 'kendall', 'ConstraintsBounds_Ken_Astronauts',
                         'statistics.csv'),
            'Law': Path('.', 'experiments', 'constraints_bounds', 'kendall', 'ConstraintsBounds_Ken_Law',
                        'statistics.csv'),
            'MEPS': Path('.', 'experiments', 'constraints_bounds', 'kendall', 'ConstraintsBounds_Ken_MEPS',
                         'statistics.csv'),
            'TPC-H': Path('.', 'experiments', 'constraints_bounds', 'kendall', 'ConstraintsBounds_Ken_TPCH',
                         'statistics.csv'),
        }
    },
    'predicate_kind': {
        'JAC': {
            'Astr': Path('.', 'experiments', 'Predicate', 'max_original',
                         'Predicate_MO_Astronauts', 'statistics.csv'),
            'Law': Path('.', 'experiments', 'Predicate', 'max_original', 'Predicate_MO_Law',
                        'statistics.csv'),
            # 'MEPS': Path('.', 'experiments', 'Predicate', 'max_original', 'Predicate_MO_MEPS',
            #              'statistics.csv'),
        },
        'QD': {
            'Astr': Path('.', 'experiments', 'Predicate', 'query_distance',
                         'Predicate_QD_Astronauts', 'statistics.csv'),
            'Law': Path('.', 'experiments', 'Predicate', 'query_distance', 'Predicate_QD_Law',
                        'statistics.csv'),
            # 'MEPS': Path('.', 'experiments', 'Predicate', 'query_distance', 'Predicate_QD_MEPS',
            #              'statistics.csv'),
        },
        'KEN': {
            'Astr': Path('.', 'experiments', 'Predicate', 'kendall', 'Predicate_Ken_Astronauts',
                         'statistics.csv'),
            'Law': Path('.', 'experiments', 'Predicate', 'kendall', 'Predicate_Ken_Law',
                        'statistics.csv'),
            # 'MEPS': Path('.', 'experiments', 'Predicate', 'kendall', 'Predicate_Ken_MEPS',
            #              'statistics.csv'),
        }
    },
}

USEFUL_SIGN_TO_COLOR_INDEX = {
    'MO': UsefulMethod.JACCARD_DISTANCE,
    'KEN': UsefulMethod.KENDALL_DISTANCE,
    'JAC': UsefulMethod.JACCARD_DISTANCE,
    'QD': UsefulMethod.QUERY_DISTANCE
}


def plot_graphs_per_dir():
    for x_axis, useful in STATISTICS.items():
        for useful_sign, datasets in useful.items():
            for dataset_sign, path in datasets.items():
                if os.path.exists(path):
                    df = pd.read_csv(path)
                    color_index = USEFUL_SIGN_TO_COLOR_INDEX[useful_sign]
                    plot_duration_from_df(df, x_axis, color_index, dataset_sign,
                                          f'duration = f({x_axis}), {color_index}', f'{dataset_sign}-{useful_sign}')
                else:
                    print(f'Skip {x_axis}, {useful_sign}, {dataset_sign} -- because {path} does not exist!')


def _group_by_dataset(useful_dict):
    result = defaultdict(dict)
    for useful_sign, datasets in useful_dict.items():
        for dataset_sign, path in datasets.items():
            result[dataset_sign][useful_sign] = path
    return result


class GraphKind(Enum):
    LINE = 1
    BAR = 2


GRAPH_KIND_TO_LABEL = {
    GraphKind.LINE: ['K', 'max_deviation', 'number_of_constraints'],
    GraphKind.BAR: ['constraints_bounds', 'predicate_kind']
}


def plot_duration_for_combined_useful_for_each_dataset(log_scale=False):
    y_label = 'duration[sec]'

    for x_label, useful_dict in STATISTICS.items():
        datasets = _group_by_dataset(useful_dict)
        # print(datasets)
        should_show_legend = True
        for dataset_sign, useful_to_path in datasets.items():
            plt.figure(figsize=(8, 4))
            dfs = dict()
            for useful_sign, path in useful_to_path.items():
                if os.path.exists(path):
                    dfs[useful_sign] = pd.read_csv(path)
                else:
                    print(f'Skip {x_label}, {useful_sign}, {dataset_sign} -- because {path} does not exist!')
            index, x = None, None
            plot_number = -1
            for useful_sign, df in sorted(dfs.items(), key=lambda item: PLOT_ORDER.index(item[0])):
                plot_number += 1
                x, y_setup, y_solver, y_total, deviations = get_axises_from_df(df, x_label)
                index = _get_index(x)
                color_index = USEFUL_SIGN_TO_COLOR_INDEX[useful_sign]
                if x_label in GRAPH_KIND_TO_LABEL[GraphKind.LINE]:
                    plot_lines_duration_graph(index, y_setup, y_total, color_index, useful_sign, annotations=deviations)
                else:
                    plot_bar_duration_graph(index, y_setup, y_solver, color_index, useful_sign, annotations=deviations,
                                            gap_number=plot_number)
            if index is None:
                continue
            plot_features(index, x, READABLE_LABLES[x_label], 'Duration [sec]', f'duration = f({x_label}), {dataset_sign}', should_show_legend=should_show_legend)
            should_show_legend = False

            combined_output_dir = Path(OUTPUT_DIR, 'combined_useful_by_dataset')
            x_output_dir = Path(combined_output_dir, x_label)
            if not os.path.exists(combined_output_dir):
                os.makedirs(combined_output_dir)
            if not os.path.exists(x_output_dir):
                os.makedirs(x_output_dir)

            output_dir = Path(OUTPUT_DIR, 'combined_useful_by_dataset', x_label, 'linear_scale')
            scale = "linear_scaled"
            if log_scale:
                plt.yscale('log')
                output_dir = Path(OUTPUT_DIR, 'combined_useful_by_dataset', x_label, 'log_scale')
                scale = "log_scaled"

            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            plt.savefig(Path(output_dir, f'{dataset_sign}-CombUseful__{y_label}_by_{x_label}__{scale}__lines.pdf'),
                        bbox_inches='tight', format="pdf")
            plt.clf()
            plt.close()
            # plt.show()


USEFUL_STRING_TO_USEFUL_METHOD = {
    'JACCARD_DISTANCE': UsefulMethod.JACCARD_DISTANCE,
    'KENDALL_DISTANCE': UsefulMethod.KENDALL_DISTANCE,
    'QUERY_DISTANCE': UsefulMethod.QUERY_DISTANCE,
    'MAX_ORIGINAL': UsefulMethod.MAX_ORIGINAL
}

SHORT_STRINGS = {
    'JACCARD_DISTANCE': 'JAC',
    'KENDALL_DISTANCE': 'KEN',
    'QUERY_DISTANCE': 'QD',
    'MAX_ORIGINAL': 'JAC'
}

READABLE_LABLES = {
    'K': '$k^*$',
    'max_deviation': 'Maximum deviation ($\\varepsilon$)',
    'number_of_constraints': 'Number of Constraints',
    'constraints_bounds': 'Types of Constraints',
    'predicate_kind': 'Type of Predicates',
    'duration[sec]': 'Duration [sec]'
}

# def plot_algorithm_comparison_per_useful(log_scale=False):
#     y_label = 'duration[sec]'
#     x_label = 'algorithm'
#     index = None

#     useful_to_dataset = defaultdict(dict)
#     for dataset_sign, path in ALGORITHM_COMPARISON_STATISTICS:
#         dataset_df = None
#         if os.path.exists(path):
#             dataset_df = pd.read_csv(path)
#         else:
#             print(f'Skip {dataset_sign} -- because {path} does not exist!')

#         useful_methods = pd.unique(dataset_df['useful_method'])
#         for useful_method in useful_methods:
#             df = dataset_df[dataset_df['useful_method'] == useful_method]
#             useful_to_dataset[useful_method][dataset_sign] = df

#     count_bars = 0
#     should_show_legend = True
#     for useful_method, dataset in useful_to_dataset.items():
#         for dataset_sign, df in dataset.items():
#             y_total = df.groupby([x_label], sort=False)['total_duration[sec]'].mean()
#             y_setup = df.groupby([x_label], sort=False)['setup_duration[sec]'].mean()
#             y_solver = df.groupby([x_label], sort=False)['solver_duration[sec]'].mean()
#             x = df.groupby(x_label, sort=False)[x_label].first()

#             index = _get_index(x) - 0.1 * count_bars
#             plot_bar_duration_graph(index, y_setup, y_solver, dataset_sign, dataset_sign, width=0.1)
#             count_bars += 1

#         plot_features(index, ['MILP_OPT', 'MILP'], x_label, y_label, f'duration = f({x_label}), {useful_method}',
#                       legend_loc='best', should_show_legend=should_show_legend)
#         should_show_legend = False

#         output_dir = Path(OUTPUT_DIR, 'algorithms_comparison')
#         if not os.path.exists(output_dir):
#             os.makedirs(output_dir)
#         scale = "linear_scaled"
#         if log_scale:
#             scale = 'log_scaled'
#             plt.yscale('log')
#         plt.savefig(Path(output_dir, f'CombDatasets-{useful_method}__{y_label}_by_{x_label}__{scale}__lines.pdf'),
#                     bbox_inches='tight', format="pdf")
#         plt.clf()
#         # plt.show()


def plot_algorithm_comparison_per_dataset(log_scale=False):
    y_label = 'duration[sec]'
    x_label = 'algorithm'
    index = None

    count_bars = 0
    should_show_legend = True
    for i in range(len(ALGORITHM_COMPARISON_STATISTICS)):
        plt.figure(figsize=(8, 4))
        dataset_sign, path = ALGORITHM_COMPARISON_STATISTICS[i]
        dataset_df = None
        if os.path.exists(path):
            dataset_df = pd.read_csv(path)
            dataset_df = dataset_df.drop(dataset_df[(dataset_df['total_duration[sec]'] >= 3600) | (dataset_df['total_duration[sec]'] == 0)].index)
        else:
            print(f'Skip {dataset_sign} -- because {path} does not exist!')

        useful_methods = sorted(pd.unique(dataset_df['useful_method']), key=PLOT_ORDER.index)
        plot_number = 0
        for j in range(len(useful_methods)):
            useful_method = useful_methods[j]
            df = dataset_df[dataset_df['useful_method'] == useful_method]
            plot_number += 1
            x, y_setup, y_solver, y_total, deviations = get_axises_from_df(df, x_label)
            # Naive has no setup phase, so we count everything as solver time
            x = x.reset_index(drop=True)
            naive_index = x[x == 'RefinementMethod.BRUTE'].any() and x[x == 'RefinementMethod.BRUTE'].index[0]
            if naive_index:
                index = list(filter(lambda x: x != naive_index, _get_index(x)))
                color_index = USEFUL_SIGN_TO_COLOR_INDEX[SHORT_STRINGS[useful_method]]
                plot_bar_duration_graph(np.asarray(index), y_setup.iloc[index], y_solver.iloc[index], color_index, SHORT_STRINGS[useful_method], annotations=deviations.iloc[index],
                                        gap_number=plot_number)
                plot_bar_duration_graph(np.asarray([naive_index]), y_setup.iloc[naive_index], y_solver.iloc[naive_index], color_index, SHORT_STRINGS[useful_method], annotations=deviations.iloc[naive_index],
                        gap_number=plot_number, is_split=False)
            else:
                index = _get_index(x)
                color_index = USEFUL_SIGN_TO_COLOR_INDEX[SHORT_STRINGS[useful_method]]
                plot_bar_duration_graph(index, y_setup, y_solver, color_index, SHORT_STRINGS[useful_method], annotations=deviations,
                                        gap_number=plot_number)
        if index is None:
            continue

        mapping = {
            'MILP': 'MILP',
            'MILP_OPT': 'MILP+opt',
            'BRUTE': 'Naïve',
            'BRUTE_PROV': 'Naïve+prov'
        }
        index = _get_index(x) + 0.2
        plot_features(index, [mapping[val.split('.')[1]] for val in x], 'Algorithm', 'Duration [sec]', f'duration = f({x_label}), {dataset_sign}', should_show_legend=should_show_legend)

        # for j in range(len(useful_methods)):
        #     useful_method = useful_methods[j]
        #     df = dataset_df[dataset_df['useful_method'] == useful_method]

        #     y_total = df.groupby([x_label], sort=False)['total_duration[sec]'].mean()
        #     y_setup = df.groupby([x_label], sort=False)['setup_duration[sec]'].mean()
        #     y_solver = df.groupby([x_label], sort=False)['solver_duration[sec]'].mean()
        #     deviations = df.groupby([x_label], sort=False)['deviation'].mean()
        #     x = df.groupby(x_label, sort=False)[x_label].first()

        #     color_index = USEFUL_STRING_TO_USEFUL_METHOD[useful_method]

        #     index = _get_index(x) - 0.1 * count_bars
        #     plot_bar_duration_graph(index, y_setup, y_solver, color_index, SHORT_STRINGS[useful_method], annotations=deviations, width=0.1)
        #     count_bars += 1



        # index = _get_index(x) - 0.2
        # plot_features(index, [mapping[val.split('.')[1]] for val in x], 'Algorithm', 'Duration [sec]',
        #               f'duration = f({x_label}), {dataset_sign}', legend_loc='best', should_show_legend=should_show_legend)
        should_show_legend = False

        output_dir = Path(OUTPUT_DIR, 'algorithms_comparison')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        scale = "linear_scaled"
        if log_scale:
            scale = 'log_scaled'
            plt.yscale('log')
        plt.savefig(Path(output_dir, f'{dataset_sign}-CombUseful__{y_label}_by_{x_label}__{scale}__lines.pdf'),
                    bbox_inches='tight', format="pdf")
        plt.clf()
        plt.close()
        # plt.show()

def plot_data_size_comparison_per_useful(log_scale=False):
    y_label = 'duration[sec]'
    x_label = 'data_size'
    index = None

    count_bars = 0
    should_show_legend = True
    for i in range(len(DATA_SIZE_COMPARISON_STATISTICS)):
        plt.figure(figsize=(8, 4))
        dataset_sign, path, unit = DATA_SIZE_COMPARISON_STATISTICS[i]
        dataset_df = None
        if os.path.exists(path):
            dataset_df = pd.read_csv(path)
        else:
            print(f'Skip {dataset_sign} -- because {path} does not exist!')

        useful_methods = sorted(pd.unique(dataset_df['useful_method']), key=PLOT_ORDER.index)
        for j in range(len(useful_methods)):
            useful_method = useful_methods[j]
            df = dataset_df[dataset_df['useful_method'] == useful_method]

            y_total = df.groupby([x_label], sort=False)['total_duration[sec]'].mean()
            y_setup = df.groupby([x_label], sort=False)['setup_duration[sec]'].mean()
            y_solver = df.groupby([x_label], sort=False)['solver_duration[sec]'].mean()
            deviations = df.groupby([x_label], sort=False)['deviation'].mean()
            x = df.groupby(x_label, sort=False)[x_label].first()
            # Assumes there are two labels in statistics.csv: data size and lineage classes
            lineage_classes = df.groupby(x_label,sort=False)['lineage_classes'].first()

            color_index = USEFUL_STRING_TO_USEFUL_METHOD[useful_method]

            index = _get_index(x) - 0.1 * count_bars
            # since overlapping & the same for all
            plot_lines_duration_graph(index, y_setup, y_total, color_index, SHORT_STRINGS[useful_method], annotations=deviations[:10])
            # plot_bar_duration_graph(index, y_setup, y_solver, color_index, useful_method, width=0.1)
            count_bars += 1

        plot_features(index, [f'{s}\n{l}' for s, l in zip(x, lineage_classes)], f'Data Size [{unit}]\nLineage Classes', 'Duration [sec]',
                        f'duration = f({x_label}), {dataset_sign}', legend_loc='upper left', should_show_legend=should_show_legend)
        should_show_legend = False

        output_dir = Path(OUTPUT_DIR, 'data_size')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        scale = "linear_scaled"
        if log_scale:
            scale = 'log_scaled'
            plt.yscale('log')
        plt.savefig(Path(output_dir, f'{dataset_sign}-CombUseful__{y_label}_by_{x_label}__{scale}__lines.pdf'),
                    bbox_inches='tight', format="pdf")
        plt.clf()
        plt.close()
        # plt.show()

def plot_lineage_classes_comparison_per_useful(log_scale=False):
    y_label = 'duration[sec]'
    x_label = 'lineage_classes'
    index = None

    count_bars = 0
    should_show_legend = True
    for i in range(len(LINEAGE_CLASSES_COMPARISON_STATISTICS)):
        plt.figure(figsize=(8, 4))
        dataset_sign, path = LINEAGE_CLASSES_COMPARISON_STATISTICS[i]
        dataset_df = None
        if os.path.exists(path):
            dataset_df = pd.read_csv(path)
        else:
            print(f'Skip {dataset_sign} -- because {path} does not exist!')

        useful_methods = pd.unique(dataset_df['useful_method'])
        for j in range(len(useful_methods)):
            useful_method = useful_methods[j]
            df = dataset_df[dataset_df['useful_method'] == useful_method]

            y_total = df.groupby([x_label], sort=False)['total_duration[sec]'].mean()
            y_setup = df.groupby([x_label], sort=False)['setup_duration[sec]'].mean()
            y_solver = df.groupby([x_label], sort=False)['solver_duration[sec]'].mean()
            deviations = df.groupby([x_label], sort=False)['deviation'].mean()
            x = df.groupby(x_label, sort=False)[x_label].first()

            color_index = USEFUL_STRING_TO_USEFUL_METHOD[useful_method]

            index = _get_index(x) - 0.1 * count_bars
            # since overlapping & the same for all
            plot_lines_duration_graph(index, y_setup, y_total, color_index, SHORT_STRINGS[useful_method], annotations=deviations[:10])
            # plot_bar_duration_graph(index, y_setup, y_solver, color_index, useful_method, width=0.1)
            count_bars += 1

        plot_features(index, x, '\# of Lineage Classes', 'Duration [sec]',
                      f'duration = f({x_label}), {dataset_sign}', legend_loc='upper left', should_show_legend=should_show_legend)
        should_show_legend = False

        output_dir = Path(OUTPUT_DIR, 'lineage_classes')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        scale = "linear_scaled"
        if log_scale:
            scale = 'log_scaled'
            plt.yscale('log')
        plt.savefig(Path(output_dir, f'{dataset_sign}-CombUseful__{y_label}_by_{x_label}__{scale}__lines.pdf'),
                    bbox_inches='tight', format="pdf")
        plt.clf()
        plt.close()
        # plt.show()

# def plot_algorithm_comparison(log_scale=False):
#     y_label = 'duration[sec]'
#     x_label = 'algorithm'
#     index = None
#
#     count_bars = 0
#     for i in range(len(ALGORITHM_COMPARISON_STATISTICS)):
#         dataset_sign, path = ALGORITHM_COMPARISON_STATISTICS[i]
#         dataset_df = None
#         if os.path.exists(path):
#             dataset_df = pd.read_csv(path)
#         else:
#             print(f'Skip {dataset_sign} -- because {path} does not exist!')
#
#         useful_methods = pd.unique(dataset_df['useful_method'])
#         for j in range(len(useful_methods)):
#             useful_method = useful_methods[j]
#             df = dataset_df[dataset_df['useful_method'] == useful_method]
#
#             y_total = df.groupby([x_label], sort=False)['total_duration[sec]'].mean()
#             y_setup = df.groupby([x_label], sort=False)['setup_duration[sec]'].mean()
#             y_solver = df.groupby([x_label], sort=False)['solver_duration[sec]'].mean()
#             x = df.groupby(x_label, sort=False)[x_label].first()
#
#             color_index = USEFUL_STRING_TO_USEFUL_METHOD[useful_method]
#
#             index = _get_index(x) - 0.1 * count_bars
#             plot_bar_duration_graph(index, y_setup, y_solver, color_index, f'{dataset_sign}_{useful_method}', width=0.1)
#             count_bars += 1
#
#
#     plot_features(index, [val.split('.')[1] for val in x], x_label, y_label, f'duration = f({x_label})', legend_loc='best')
#
#     output_dir = Path(OUTPUT_DIR, 'algorithms_comparison')
#     scale = 'log_scaled'
#     plt.yscale('log')
#     # scale = "linear_scaled"
#     # if log_scale:
#     #     plt.yscale('log')
#     #     scale = "log_scaled"
#     plt.savefig(Path(output_dir, f'CombDataset-CombUseful__{y_label}_by_{x_label}__{scale}__lines.png'), bbox_inches='tight')
#     plt.show()
#     # for x_label, useful_dict in STATISTICS.items():
#     #     datasets = _group_by_dataset(useful_dict)
#     #     print(datasets)
#     #     for dataset_sign, useful_to_path in datasets.items():
#     #         dfs = dict()
#     #         for useful_sign, path in useful_to_path.items():
#     #             if os.path.exists(path):
#     #                 dfs[useful_sign] = pd.read_csv(path)
#     #             else:
#     #                 print(f'Skip {x_label}, {useful_sign}, {dataset_sign} -- because {path} does not exist!')
#     #         index = None
#     #         for useful_sign, df in dfs.items():
#     #             x, y_setup, y_solver, y_total = get_axises_from_df(df, x_label)
#     #             index = _get_index(x)
#     #             color_index = USEFUL_SIGN_TO_COLOR_INDEX[useful_sign]
#     #             plot_lines_duration_graph(index, y_setup, y_total, color_index, useful_sign)
#     #         plot_features(index, x, x_label, y_label, f'duration = f({x_label}), {dataset_sign}')
#     #
#     #         output_dir = Path(OUTPUT_DIR, 'combined_useful_by_dataset', 'linear_scale')
#     #         scale = "linear_scaled"
#     #         if log_scale:
#     #             plt.yscale('log')
#     #             output_dir = Path(OUTPUT_DIR, 'combined_useful_by_dataset', 'log_scale')
#     #             scale = "log_scaled"
#     #         plt.savefig(Path(output_dir, f'{dataset_sign}-CombUseful__{y_label}_by_{x_label}__{scale}__lines.png'), bbox_inches='tight')
#     #
#     #         plt.show()


if __name__ == '__main__':
    # # plot_graphs_per_dir()
    plot_duration_for_combined_useful_for_each_dataset()
    plot_duration_for_combined_useful_for_each_dataset(True)
    plot_data_size_comparison_per_useful()
    # plot_lineage_classes_comparison_per_useful()
    # # plot_algorithm_comparison_per_useful()
    plot_algorithm_comparison_per_dataset()
    plot_algorithm_comparison_per_dataset(True)
