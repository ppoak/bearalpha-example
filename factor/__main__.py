import os
import argparse
import bearalpha as ba
from .tools import *
from .barrastyle import *


def run(args):
    start = args.start
    end = args.end
    factor = args.factor
    benchmark = args.benchmark
    benchmark_data = None
    stock = ba.Stock(ba.Cache().get('local'))
    
    if args.args is None:
        args = BARRASTYLE[factor]['args']
    else:
        args = args.args
    factor = BARRASTYLE[factor]['factor'](*args)
    store_dir = ba.Cache().get('factor_report_path')

    if not os.path.exists(f'{store_dir}/{factor}'):
        os.mkdir(f'{store_dir}/{factor}')
    factor_matrix: ba.DataFrame = factor_data(factor, start, end)
    # This may change in the future
    price = ba.read_parquet(ba.Cache().get('vwap_path'))
    price.columns = price.columns.map(lambda x: x[3:] + ('.XSHG' if x[:2] == 'sh' else '.XSHE'))
    grouper = group_mapping(start, end)
    if benchmark is not None:
        benchmark_data = stock.index_market_daily(start, end, code=benchmark, fields='close')
        benchmark_data.name = benchmark

    factor_matrix.factester.analyze(
        price=price, 
        grouper=grouper,
        benchmark=benchmark_data,
        periods=[5, 10, 15, 20],
        commission=0,
        image_path=f'{store_dir}/{factor}/{factor}.pdf',
        data_path=f"{store_dir}/{factor}/{factor}.xlsx",
        )

def main():
    usage = "python -m factor -f factor [-s start] [-e end] [-a *args]"
    parser = argparse.ArgumentParser(description='Factor analyzer cli api', usage=usage)
    parser.add_argument('-s', '--start', type=str, default='20170101', help='Back test start time')
    parser.add_argument('-e', '--end', type=str, default='20220131', help='Back test end time')
    parser.add_argument('-f', '--factor', type=str, required=True, help='Factor name you want to test')
    parser.add_argument('-a', '--args', nargs='+', default=None, type=int, help='Arguments passed to factor handler')
    parser.add_argument('-b', '--benchmark', type=str, default=None, help='Assign benchmark plot')

    # This may seem to be unnecessary, 
    # but just keep it for the sake of uniform code style
    parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()