# ---
import matplotlib.pyplot as plt
import quool as ql
import pandas as pd
from scipy.stats import norm
import numpy as np

# ---
relation = pd.read_excel('Researches/FinancialRiskRatio/relation.xlsx', usecols=['from', 'to']).dropna()
relation_list = set(relation['from'].to_list() + relation['to'].to_list())
balance_indicator = list(filter(lambda x: x.startswith('balance'), relation_list))
balance_indicator = list(map(lambda x: x.split('.')[1], balance_indicator))
income_indicator = list(filter(lambda x: x.startswith('income'), relation_list))
income_indicator = list(map(lambda x: x.split('.')[1] , income_indicator))
cashflow_indicator = list(filter(lambda x: x.startswith('cashflow'), relation_list))
cashflow_indicator = list(map(lambda x: x.split('.')[1], cashflow_indicator))
ttm_indicator = list(filter(lambda x: x.startswith('ttm'), relation_list))
ttm_indicator = list(map(lambda x: x.split('.')[1], ttm_indicator))

# ---
'''
balance = ql.Filer.read_csv_directory('/Users/oak/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/594c89b5881202d252804932a6a1aa29/Message/MessageTemp/f1d2258a4159f4e12dea50db99871185/File/stock_balance', index_col='report_date', perspective='asset',
                                      parse_dates=True, usecols=balance_indicator + ['statement_type', 'report_date'])
income = ql.Filer.read_csv_directory('/Users/oak/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/594c89b5881202d252804932a6a1aa29/Message/MessageTemp/f1d2258a4159f4e12dea50db99871185/File/stock_income', index_col='report_date', perspective='asset',
                                     parse_dates=True, usecols=income_indicator + ['statement_type', 'report_date'])
cashflow = ql.Filer.read_csv_directory('/Users/oak/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/594c89b5881202d252804932a6a1aa29/Message/MessageTemp/f1d2258a4159f4e12dea50db99871185/File/stock_cashflow', index_col='report_date', perspective='asset',
                                     parse_dates=True, usecols=cashflow_indicator + ['statement_type', 'report_date'])
ttm = ql.Filer.read_csv_directory('/Users/oak/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/594c89b5881202d252804932a6a1aa29/Message/MessageTemp/f1d2258a4159f4e12dea50db99871185/File/stock_ttm', index_col='stock_id', perspective='datetime',
                                     parse_dates=['report_date'], usecols=ttm_indicator + ['stock_id', 'report_date'])
balance = balance[balance.statement_type == 408001000].drop('statement_type', axis=1)
income = income[income.statement_type == 408001000].drop('statement_type', axis=1)
cashflow = cashflow[cashflow.statement_type == 408001000].drop('statement_type', axis=1)
ttm = ttm.reset_index().set_index(['report_date', 'stock_id']).drop(
    'level_0', axis=1).sort_index().dropna(how='all')
ttm = ttm[~ttm.index.duplicated(keep='last')]
balance.to_parquet('data.nosync/balance')
income.to_parquet('data.nosync/income')
cashflow.to_parquet('data.nosync/cashflow')
ttm.to_parquet('data.nosync/ttm')
'''

# ---
balance = pd.read_parquet('data.nosync/balance')
income = pd.read_parquet('data.nosync/income')
cashflow = pd.read_parquet('data.nosync/cashflow')
industry = pd.read_parquet('data.nosync/industry')
ttm = pd.read_parquet('data.nosync/ttm')

# ---
income_diff = income.converter.cum2diff(lambda x: x[0].year)
income = income_diff.groupby(level=1).rolling(4).sum().droplevel(0).sort_index().dropna(how='all')

# ---
industry = industry.groupby([pd.Grouper(level=0, freq='q'), pd.Grouper(level=1)]).last()

# ---
common_index = ttm.index.intersection(income.index).intersection(
    cashflow.index).intersection(industry.index).intersection(balance.index)
balance = balance.loc[common_index]
income = income.loc[common_index]
cashflow = cashflow.loc[common_index]
ttm = ttm.loc[common_index]

# ---
net_profit = ttm.loc[:, 'net_profit_ttm']
net_profit_growth = net_profit.groupby(level=1).shift(-1) / net_profit - 1
net_profit_growth_growth = net_profit_growth.groupby(level=1).shift(-1) / net_profit_growth - 1

# ---
ratio = pd.DataFrame()
for i, rel in relation.iterrows():
    from_table = eval(rel['from'].split('.')[0])
    from_col = rel['from'].split('.')[1]
    from_var = from_table[from_col]
    from_var = from_var[~from_var.index.duplicated(keep='first')]
    to_table = eval(rel['to'].split('.')[0])
    to_col = rel['to'].split('.')[1]
    to_var = to_table[to_col]
    to_var = to_var[~to_var.index.duplicated(keep='first')]
    ratio[i] = from_var / to_var

# 尝试减少数据量
ratio = ratio[ratio.columns[(ratio.count() / ratio.shape[0]) > 0.5]]
# 数据清洗
ratio_processed = ratio.preprocessor.standarize('zscore')\
    .preprocessor.fillna('mean', grouper=industry.group)\
    .preprocessor.deextreme('mad')

# ---
def calc_unit(data):
    def _calc_inner_ind(_data):
        res = 1 - norm.sf(_data) * 2
        res = pd.DataFrame(res, index=_data.index, columns=_data.columns)
        return res.groupby(level=1).last().mean(axis=1)

    # the latest industry infomation
    idx = data.index.get_level_values(0)[-1]
    currect_group = industry.loc[idx].group.to_dict()

    dev = data.groupby(lambda x: currect_group.get(x[1], '')).apply(_calc_inner_ind)
    score = dev.abs().groupby(level=1).last()
    return score

score = ratio_processed.calculator.rolling(window=30, func=calc_unit)

# ---
industry_score = score.groupby([pd.Grouper(level=0), industry.group]).mean()
industry_score = industry_score.loc[industry_score.index.get_level_values(1) != '']

# ---
ic_gg = score.describer.ic(net_profit_growth_growth)
ic_g = score.describer.ic(net_profit_growth)

# ---
ic_g.tester.sigtest()

# ---
ic_gg.tester.sigtest()

# ---
def industry_forward(data):
    last_date = data.index.get_level_values(0)[-1]
    first_date = data.index.get_level_values(0)[0]
    common_company = data.loc[first_date].index.intersection(data.loc[last_date].index)
    last_sum = data.loc[last_date, common_company].sum()
    first_sum = data.loc[first_date, common_company].sum()
    if first_sum == 0:
        return np.nan
    return last_sum / first_sum - 1

net_profit_growth_industry = net_profit.groupby(industry.group).apply(lambda x: x.calculator.rolling(2, industry_forward))
net_profit_growth_industry = net_profit_growth_industry.swaplevel().sort_index()
net_profit_growth_industry = net_profit_growth_industry.loc[net_profit_growth_industry.index.get_level_values(1) != '']
net_profit_growth_industry = net_profit_growth_industry.preprocessor.deextreme('mad').preprocessor.standarize('zscore')
net_profit_growth_industry = net_profit_growth_industry.groupby(level=1).shift(-1)[0]

net_profit_growth_growth_industry = net_profit_growth_industry.groupby(level=1).shift(-1) / net_profit_growth_industry - 1
net_profit_growth_growth_industry = net_profit_growth_growth_industry.preprocessor.deextreme('mad').preprocessor.standarize('zscore')

# ---
def reverso_record(code):
    data = pd.read_html(f'https://vip.stock.finance.sina.com.cn/corp/go.php/vGP_GetOutOfLine/stockid/{code}.phtml')
    data = data[13]
    data

# ---
with ql.Gallery(1, 1, figsize=(12, 8)) as g:
    draw_data = pd.concat([net_profit_growth_industry, industry_score], axis=1).dropna()
    draw_data = draw_data.groupby(level=1).rolling(4).mean().droplevel(0).sort_index()
    draw_data.columns = ['net_profit_growth_growth', 'industry_score']
    draw_data.drawer.draw('bar', indicator='net_profit_growth_growth', asset='zx_steel', ax=g.axes[0, 0], color='orange')
    draw_data.drawer.draw('line', indicator='industry_score', asset='zx_steel', ax=g.axes[0, 0].twinx())
