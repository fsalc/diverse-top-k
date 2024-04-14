import pandas as pd
from pathlib import Path
import sys
import datetime as dt

DIR = Path('~','ranking-refinements','ranking_refinements','data','TPCH','SCALE')

def adjuct(tpch_dir):
    df = pd.read_csv(Path(tpch_dir, 'lineitem.csv'), sep='|')
    df['REVENUE1'] = df['EXTENDEDPRICE'] * df['DISCOUNT']
    df['REVENUE2'] = df['EXTENDEDPRICE'] * (1 - df['DISCOUNT'])
    df['SHIPDATE'] = (pd.to_datetime(df['SHIPDATE'], format='%Y-%m-%d') - dt.datetime(1970, 1, 1)).dt.total_seconds()
    df['COMMITDATE'] = (pd.to_datetime(df['COMMITDATE'], format='%Y-%m-%d') - dt.datetime(1970, 1, 1)).dt.total_seconds()
    df['RECEIPTDATE'] = (pd.to_datetime(df['RECEIPTDATE'], format='%Y-%m-%d') - dt.datetime(1970, 1, 1)).dt.total_seconds()
    df.to_csv(Path(tpch_dir, 'lineitem.csv'))
    # df_lineitem['SHIPDATE'] = df_lineitem['SHIPDATE'].astype('int64')//1e9
    # df_lineitem['COMMITDATE'] = df_lineitem['COMMITDATE'].astype('int64')//1e9
    # df_lineitem['RECEIPTDATE'] = df_lineitem['RECEIPTDATE'].astype('int64')//1e9

    df = pd.read_csv(Path(tpch_dir, 'customer.csv'), sep='|')
    df.to_csv(Path(tpch_dir, 'customer.csv'))

    df = pd.read_csv(Path(tpch_dir, 'nation.csv'), sep='|')
    df.to_csv(Path(tpch_dir, 'nation.csv'))

    df = pd.read_csv(Path(tpch_dir, 'orders.csv'), sep='|')
    df['ORDERDATE'] = (pd.to_datetime(df['ORDERDATE'], format='%Y-%m-%d') - dt.datetime(1970, 1, 1)).dt.total_seconds()
    # df_lineitem['RECEIPTDATE'] = df_lineitem['RECEIPTDATE'].astype('int64') // 1e9
    df.to_csv(Path(tpch_dir, 'orders.csv'))

    df = pd.read_csv(Path(tpch_dir, 'part.csv'), sep='|')
    df.to_csv(Path(tpch_dir, 'part.csv'))

    df = pd.read_csv(Path(tpch_dir, 'partsupp.csv'), sep='|')
    df.to_csv(Path(tpch_dir, 'partsupp.csv'))

    df = pd.read_csv(Path(tpch_dir, 'region.csv'), sep='|')
    df.to_csv(Path(tpch_dir, 'region.csv'))

    df = pd.read_csv(Path(tpch_dir, 'supplier.csv'), sep='|')
    df.to_csv(Path(tpch_dir, 'supplier.csv'))


if __name__ == '__main__':
    tpch_dir = DIR
    if len(sys.argv) >= 2:
        tpch_dir = sys.argv[1]
    adjuct(tpch_dir)
