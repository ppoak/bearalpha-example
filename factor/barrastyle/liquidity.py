import bearalpha as ba
from ..core import *


class FactorLiquidity(FactorBase):
    def __init__(self, name):
        super().__init__(name)
        self.kalss = 'liquidity'


class NonLiquidityImpact(FactorLiquidity):
    def __init__(self, period):
        self.period = period
        name = 'nonliquidityimpact_' + str(period)
        super().__init__(name)
    
    def calculate(self, date):
        last_date = ba.date_range(end=date, periods=self.period, freq=ba.CBD)[0]
        prices = self.datasource.market_daily(last_date, date, fields=['adjclose', 'total_turnover'])
        change = (prices['adjclose'] - prices['adjclose'].groupby(level=1).shift(1)).abs()
        self.factor = (change / prices['total_turnover']).groupby(level=1).mean()


class TurnoverMA(FactorLiquidity):
    def __init__(self, period):
        self.period = period
        name = 'turnoverma_' + str(period)
        super().__init__(name)
    
    def calculate(self, date):
        last_date = ba.date_range(end=date, periods=self.period, freq=ba.CBD)[0]
        turnover = self.datasource.derivative_indicator(last_date, date, fields='turnover')
        self.factor = - turnover.groupby(level=1).mean()


class TurnoverProp(FactorLiquidity):
    """Turnover in a shorter period / turnover in a longer period
    
    TWO parameters are required, one for the shorter period, the other for the longer period
    """
    def __init__(self, short_period, long_period):
        self.short_period = short_period
        self.long_period = long_period
        name = 'turnoverprop_' + str(short_period) + '_' + str(long_period)
        super().__init__(name)
    
    def calculate(self, date):
        short_last_date = ba.date_range(end=date, periods=self.short_period, freq=ba.CBD)[0]
        long_last_date = ba.date_range(end=date, periods=self.long_period, freq=ba.CBD)[0]
        short_turnover = self.datasource.derivative_indicator(short_last_date, date, fields='turnover')
        long_turnover = self.datasource.derivative_indicator(long_last_date, date, fields='turnover')
        self.factor = short_turnover.groupby(level=1).mean() / long_turnover.groupby(level=1).mean()


class AmountPerVolume(FactorLiquidity):
    """Trading amount per percent volatility, rolling mean for a period"""
    def __init__(self, period):
        self.period = period
        self.calculate_period = self.period + 20
        name = 'amountpervolume_' + str(period)
        super().__init__(name)

    def calculate(self, date):
        volume_last_date = ba.date_range(end=date, periods=self.period, freq=ba.CBD)[0]
        price_last_date = ba.date_range(end=date, periods=self.calculate_period, freq=ba.CBD)[0]
        volume = self.datasource.market_daily(volume_last_date, date, fields='volume')

        change = self.datasource.market_daily(price_last_date, date, fields='adj_pct_change')
        volatility = change.groupby(level=1).rolling(20).std().droplevel(0).sort_index()

        self.factor = ba.log((volume / volatility).groupby(level=1).mean())


class AmountPerChangeMA(FactorLiquidity):
    """Trading amount per abs(yeild), rolling mean for a period"""
    def __init__(self, period):
        self.period = period
        name = 'amountperchangema_' + str(period)
        super().__init__(name)

    def calculate(self, date):
        last_date = ba.date_range(end=date, periods=self.period, freq=ba.CBD)[0]
        volume = self.datasource.market_daily(last_date, date, fields='volume')
        change = self.datasource.market_daily(last_date, date, fields='adj_pct_change').abs()
        self.factor = ba.log((volume / change).groupby(level=1).mean())\
            .replace(ba.inf, ba.nan).replace(-ba.inf, ba.nan).dropna()


if __name__ == "__main__":
    import time
    import matplotlib.pyplot as plt
    date = '2022-06-30'
    factor = AmountPerChangeMA(10)
    start = time.time()
    data = factor(date)
    print(f'time: {time.time() - start:.2f}s')
    print(factor)
    data.printer.display(title='factor')
    data.drawer.draw('hist', bins=100, datetime=date)
    plt.show()
