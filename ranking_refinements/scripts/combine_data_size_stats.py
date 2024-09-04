# The experiment harness currently places each experiment into its own statisitcs.csv file
# Since we want to plot the runtime vs. the data size, we combine them all into one file
# This script gathers the statistics for each data set size and combines them into one singular file

import os
import pandas as pd

SF_ROOT = 'experiments/SF/'
DATASETS = ['astronauts', 'law', 'meps', 'Q5']

DATASET_SIZES = {
    'astronauts': [
        'SF_Astronauts',
        'SF_Astronauts-200KB',
        'SF_Astronauts-300KB',
        'SF_Astronauts-400KB',
        'SF_Astronauts-500KB',
    ],
    'law': [
        'SF_Law_Students',
        'SF_Law_Students-2MB',
        'SF_Law_Students-3MB',
        'SF_Law_Students-4MB',
        'SF_Law_Students-5MB'
    ],
    'meps': [
        'SF_MEPS',
        'SF_MEPS_200',
        'SF_MEPS_300',
        'SF_MEPS_400',
        'SF_MEPS_500'
    ],
    'Q5': [
        'SF_Q5_TPCH_SF1-10',
        'SF_Q5_TPCH_SF2-10',
        'SF_Q5_TPCH_SF3-10',
        'SF_Q5_TPCH_SF4-10',
        'SF_Q5_TPCH_SF5-10',
        'SF_Q5_TPCH_SF6-10',
        'SF_Q5_TPCH_SF7-10',
        'SF_Q5_TPCH_SF8-10',
        'SF_Q5_TPCH_SF9-10',
        'SF_Q5_TPCH_SF10-10'
    ]
}

# TODO: Ideally this should be measured from the dataset itself, but since we use
# static workloads, we just measure the number of lineage classes and include them as a constant here

DATASET_LINEAGE_CLASSES = {
    'astronauts': [
        199,
        434,
        591,
        673,
        754
    ],
    'law': [
        237,
        266,
        277,
        290,
        284
    ],
    'meps': [
        838,
        942,
        963,
        978,
        993
    ],
    'Q5': [
        5,
        5,
        5,
        5,
        5,
        5,
        5,
        5,
        5,
        5
    ]
}

def combine_data_size_stats(dataset, sizes, lineage_classes):
    dfs = []
    for size, num_lineage_classes in zip(sizes, lineage_classes):
        size_df = pd.read_csv(os.path.join(os.getcwd(), SF_ROOT, dataset, size, 'statistics.csv'))
        # Rename query label column to data_size in case it wasn't done
        size_df.columns.values[-4] = 'data_size'
        # Add column next to data_size with lineage_classes
        size_df = size_df.assign(lineage_classes=num_lineage_classes)
        # Append with other dataframes
        dfs.append(size_df)
    # Combine all into single dataframe
    return pd.concat(dfs, ignore_index=True, sort=False)

if __name__ == '__main__':
    if not os.path.exists(os.path.join(os.getcwd(), SF_ROOT)):
        raise Exception('Data size experiment statistics root directory not found -- are you running this script from the ranking_refinements directory?')
    
    for dataset in DATASETS:
        df = combine_data_size_stats(dataset, DATASET_SIZES[dataset], DATASET_LINEAGE_CLASSES[dataset])
        df.to_csv(os.path.join(os.getcwd(), SF_ROOT, dataset, 'statistics_test.csv'))
    
    print('Successfully aggregated all data size experiments!')