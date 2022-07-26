# ---
import numpy as np
import pandas as pd
import quool as ql

# --- Get Data
# pe data
pe = ql.Stock.derivative_indicator(start='20161230', end='20161230', fields='s_val_pe_ttm')
# price data
price = ql.Stock.market_daily(start='20170101', end='20170331', fields=['close', 'open'])
# stock pool in HS300
stock = ql.Stock.index_weight(start='20161230', end='20170331', fields='code', and_='index_code="000300.SH"')
stock = stock.reset_index().set_index(['date', 'code']).index
# select pe and price data from stock pool
pe = 1 / pe.loc[pe.index.intersection(stock)]
price = price.loc[price.index.intersection(stock)]

# --- data process
# deextreme and standarize data
pe_std = pe.preprocessor.deextreme('mad').preprocessor.standarize('zscore')
# calculate forward return in 3 month / a quater
fwd = price.converter.price2fwd(period='q', close_col='close', open_col='open')
# some preprocess
pe_std = pe_std.droplevel(0).s_val_pe_ttm.dropna()
fwd = fwd.droplevel(0).dropna()

# --- Regression for a cross section
res = pe_std.regressor.ols(y=fwd)

# --- visulization
with ql.Gallery(1, 1) as g:
    ax = g.axes[0, 0]
    pd.concat([fwd, pe_std], axis=1).\
        drawer.draw('scatter', y=0, x='s_val_pe_ttm', ylabel='forward', ax=ax)
    x = np.arange(-2, 2, 0.01)
    y = res.loc["const", "coef"] + res.loc["s_val_pe_ttm", "coef"] * x
    pd.DataFrame(y, index=x).drawer.draw('line', ax=ax, color='r')

# --- selection up 1/3 as 1, down 1/3 as 0
down = fwd.sort_values().iloc[:fwd.shape[0]//3].copy()
down.loc[:] = 0
up = fwd.sort_values().iloc[-fwd.shape[0]//3:].copy()
up.loc[:] = 1
class_ = pd.concat([up, down])
class_.name = 'up_or_down'

# ---
res = pe_std.regressor.logistic(y=class_)

# ---
with ql.Gallery(1, 1,) as g:
    ax = g.axes[0, 0]
    pd.concat([pe_std, class_], axis=1).drawer.draw('scatter', x='s_val_pe_ttm', y='up_or_down', ax=ax)
    x = np.arange(-2, 2, 0.01)
    y = 1 / (1 + np.exp(-res.loc["const", "coef"] - res.loc["s_val_pe_ttm", "coef"] * x))
    pd.DataFrame(y, index=x).drawer.draw('line', ax=ax, color='r')
