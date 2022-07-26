import bearalpha as ba
from ..core import FactorBase

class FactorTurnover(FactorBase):
    def __init__(self, name):
        super().__init__(name)
        self.klass = 'turnover'

class Turnover(FactorTurnover):
    def __init__(self, period):
        name = 'turnover_' + str(period)
        self.period = period
        super().__init__(name)

    def calculate(self, date):
        turnover = ba.Stock.derivative_indicator(date, date,
            fields='s_dq_freeturnover')['s_dq_freeturnover']
        self.factor = turnover.groupby(level=1).mean()

class BiasTurnover(FactorTurnover):
    def __init__(self, short_period, long_period):
        self.long_period = long_period
        self.short_period = short_period
        name = 'biasturnover_' + str(short_period) + '-' + str(long_period)
        super().__init__(name)
    
    def calculate(self, date):
        long_date = ba.Stock.nearby_n_trade_date(date, -self.long_period + 1)
        short_date = ba.Stock.nearby_n_trade_date(date, -self.short_period + 1)
        turnover = ba.Stock.derivative_indicator(long_date, date,
            fields='s_dq_freeturnover')['s_dq_freeturnover']
        short_mean = turnover.loc[short_date:].groupby(level=1).mean()
        long_mean = turnover.groupby(level=1).mean()
        self.factor = short_mean / long_mean
    

if __name__ == "__main__":
    import time
    factor = BiasTurnover(20, 250)
    start = time.time()
    print(factor('20200106'))
    print(f'time: {time.time() - start:.2f}s')