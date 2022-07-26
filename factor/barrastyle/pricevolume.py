import bearalpha as ba
from ..core import *

class FactorPriceVolume(FactorBase):
    def __init__(self, name):
        super().__init__(name)
        self.klass = 'pricevolume'
    

class HAlpha(FactorPriceVolume):
    def __init__(self, period):
        name = 'haplha_' + str(period)
        self.period = period
        super().__init__(name)
    
    def calculate(self, date):
        last_date = ba.date_range(end=date, periods=self.period, freq=ba.CBD)[0]
        index_price = self.datasource.index_market_daily(last_date, date,
            fields='close', code='000001.XSHG').pct_change()
        stock_price = self.datasource.market_daily(last_date, date,
            fields='adjclose').groupby(level=1).pct_change()
        self.factor = stock_price.groupby(level=1).apply(lambda x:
            # TODO: for changes in pandasquant, this should be changed
            x.droplevel(1).regressor.ols(index_price).stats.loc["const", "coef"]
            if len(x) >= 30 else ba.nan)


class HBeta(FactorPriceVolume):
    def __init__(self, period):
        name = 'hbeta_' + str(period)
        self.period = period
        super().__init__(name)
    
    def calculate(self, date):
        last_date = ba.date_range(end=date, periods=self.period, freq=ba.CBD)[0]
        index_price = self.datasource.index_market_daily(last_date, date,
            fields='close', code='000001.XSHG').pct_change()
        stock_price = self.datasource.market_daily(last_date, date,
            fields='adjclose').groupby(level=1).pct_change()
        self.factor = stock_price.groupby(level=1).apply(lambda x:
            # TODO: for changes in pandasquant, this should be changed
            x.droplevel(1).regressor.ols(index_price).stats.iloc[-1, 0]
            if len(x) >= 30 else ba.nan)


class Momentum(FactorPriceVolume):
    def __init__(self, period: int):
        name = 'momentum_' + str(period)
        self.period = period
        super().__init__(name)
    
    def calculate(self, date):
        last_date = ba.date_range(end=date, periods=self.period, freq=ba.CBD)[0]
        price_lastdate = self.datasource.market_daily(last_date, last_date,
            fields='adjclose').droplevel(0)
        price_date = self.datasource.market_daily(date, date,
            fields='adjclose').droplevel(0)
        self.factor = (price_date - price_lastdate) / price_lastdate


class WeightedMomentum(FactorPriceVolume):
    def __init__(self, period: int):
        name = 'weightedmomentum_' + str(period)
        self.period = period 
        super().__init__(name)
    
    def calculate(self, date):
        last_date = ba.date_range(end=date, periods=self.period, freq=ba.CBD)[0]
        close = self.datasource.market_daily(last_date, date, bfields='adjclose')
        change = close / close.groupby(level=1).shift(1) - 1
        turnover = self.datasource.derivative_indicator(last_date, date, fields='turnover')
        self.factor = ba.concat([change, turnover], axis=1)\
            .groupby(level=1).apply(lambda x: 
                (x['adjclose'] * x['turnover']).mean())


class ExpWeightedMomentum(FactorPriceVolume):
    def __init__(self, period: int):
        name = 'expweightedmomentum_' + str(period)
        self.period = period
        super().__init__(name)
    
    def calculate(self, date):
        last_date = ba.date_range(end=date, periods=self.period + 1, freq=ba.CBD)[0]
        change = self.datasource.market_daily(last_date, date,
            fields='adjclose').groupby(level=1).pct_change()
        turnover = self.datasource.derivative_indicator(last_date, date, fields='turnover')
        exp = ba.exp(ba.arange(-self.period + 1, 1) / self.period / 4)
        self.factor = ba.concat([change, turnover], axis=1)\
            .groupby(level=1).apply(lambda x: 
                ((x.iloc[:, 0] * x.iloc[:, 1]).iloc[1:] * exp).sum()
                if len(x) == self.period + 1 else ba.nan)


class LogPrice(FactorPriceVolume):
    def __init__(self):
        super().__init__('logprice')
    
    def calculate(self, date):
        price = self.datasource.market_daily(date, date, 
            fields='close').droplevel(0).close
        self.factor = ba.log(price)


class Amplitude(FactorPriceVolume):
    def __init__(self, period):
        self.period = period
        name = 'amplitude_' + str(period)
        super().__init__(name)
    
    def calculate(self, date):
        last_date = ba.date_range(end=date, periods=self.period, freq=ba.CBD)[0]
        price = self.datasource.market_daily(last_date, date, 
            fields=['adjhigh', 'adjlow'])
        vol = price['adjhigh'] / price['adjlow']
        self.factor = vol.groupby(level=1).apply(lambda x:
            x.droplevel(1).sort_values().iloc[-int(0.25 * self.period):].mean() -
            x.droplevel(1).sort_values().iloc[:int(0.25 * self.period)].mean()
        )

class PriceVolumeMeasuredSentiment(FactorPriceVolume):
    def __init__(self, period, multiple):
        self.period = period
        self.multiple = multiple
        name = 'price_volume_measured_sentiment_' + str(period)
        super().__init__(name)
    
    def calculate(self, date):
        rolling_window = ba.date_range(end=date, periods=self.period, freq=ba.CBD)
        assert len(rolling_window) >= 4 , "not implementable, please test it with more than 4 days' data"

        last_date = ba.date_range(end=date, periods=self.period, freq=ba.CBD)[0]
        price_matrix = self.datasource.market_daily(last_date, date, fields=['adjclose','total_turnover'])

        yeild_matrix = price_matrix.unstack().pct_change().adjclose.dropna(how='all')
        volume_diff_matrix = price_matrix.unstack().pct_change().total_turnover.dropna(how='all')

        yeild_multiple_vector = (ba.logical_or((yeild_matrix>0).all(),(yeild_matrix<0).all())*self.multiple).replace(0,1).values
        volume_multiple_vector = (ba.logical_or((volume_diff_matrix>0).all(),(volume_diff_matrix<0).all())*self.multiple).replace(0,1).values
        multiple_vector = yeild_multiple_vector*volume_multiple_vector

        factor_vector = yeild_matrix.iloc[-1]*multiple_vector
        self.factor = factor_vector
        pass


class ResidualMomentum(FactorPriceVolume):
    def __init__(self, period):
        self.period = period
        name = 'residualmomentum_' + str(period)
        super().__init__(name)

    def calculate(self, date):
        last_date = ba.date_range(end=date, periods=self.period, freq=ba.CBD)[0]
        change = self.datasource.market_daily(last_date, date, fields='adj_pct_change')
        derivative = self.datasource.derivative_indicator(last_date, date, fields=['pb_ratio_ttm', 'market_cap_2'])
        bp = 1 / derivative['pb_ratio_ttm']
        mv = derivative['market_cap_2']
        rm = self.datasource.index_market_daily(last_date, date, code='000300.XSHG', fields='pct_change')
        rm.name = 'market'

        bp_sorted = bp.groupby(level=0).apply(lambda x: x.sort_values().dropna()).droplevel(0)

        L = bp_sorted.groupby(level=0).apply(lambda x: x.iloc[:len(x)//2])\
            .droplevel(0).index.intersection(change.index)
        H = bp_sorted.groupby(level=0).apply(lambda x: x.iloc[len(x)//2:])\
            .droplevel(0).index.intersection(change.index)
        HML = change.loc[H].groupby(level=0).mean() - change.loc[L].groupby(level=0).mean()
        HML.name = 'HML'

        mv = mv.groupby('date').apply(lambda x: x.sort_values().dropna()).droplevel(0)

        S = mv.groupby(level=0).apply(lambda x: x.iloc[:len(x)//3]).droplevel(0).index.intersection(change.index)
        B = mv.groupby(level=0).apply(lambda x: x.iloc[2*len(x)//3:]).droplevel(0).index.intersection(change.index)
        SMB = change.loc[S].groupby(level=0).mean() - change.loc[B].groupby(level=0).mean()
        SMB.name = 'SMB'

        Y = change
        X = ba.concat([rm, HML, SMB],axis=1)
        regresult = Y.groupby(level=1).apply(lambda x: X.regressor.ols(y=x.droplevel(1)) if len(x) == self.period else ba.nan)
        self.factor = regresult.apply(lambda x: x.raw_result.resid.abs().sum() if (not ba.isna(x)) else ba.nan)


class AR(FactorPriceVolume):
    """sum of (daily high price - daily open price)/(daily open price - daily low price) of previous (typically 20) days"""
    def __init__(self, period):
        self.period = period
        name = 'ar_with_log_' + str(period)
        super().__init__(name)

    def calculate(self, date):
        last_date = ba.date_range(end=date, periods=self.period, freq=ba.CBD)[0]
        data = self.datasource.market_daily(last_date, date, fields=['high', 'open', 'low'])
        self.factor = ((data.high - data.open)/(data.open - data.low)).replace(ba.inf, 0).groupby(level=1).sum()


class Bias(FactorPriceVolume):
    """(last_close_price - 20_days_close_price_average)/20_days_close_price_average"""
    def __init__(self, period):
        self.period = period
        name = 'bias_' + str(period)
        super().__init__(name)

    def calculate(self, date):
        last_date = ba.date_range(end=date, periods=self.period, freq=ba.CBD)[0]
        close = self.datasource.market_daily(last_date, date, fields='close')
        today_close = close.loc[(close.index.levels[0][-1],)]
        average = close.groupby(level=1).mean()
        self.factor = (today_close - average)/average


if __name__ == "__main__":
    import time
    import matplotlib.pyplot as plt
    date = '2022-06-30'
    factor = Bias(20)
    start = time.time()
    data = factor(date)
    print(f'time: {time.time() - start:.2f}s')
    print(factor)
    data.printer.display(title='factor')
    data.drawer.draw('hist', bins=100, datetime=date)
    plt.show()

