import bearalpha as ba
from ..core import FactorBase

class FactorVolatility(FactorBase):
    def __init__(self, name):
        super().__init__(name)
        self.klass = 'volatility'

class Std(FactorVolatility):
    def __init__(self, period: int):
        name = 'std_' + str(period)
        self.period = period
        super().__init__(name)
    
    def calculate(self, date):
        last_date = ba.Stock.nearby_n_trade_date(date, -self.period)
        change = ba.Stock.market_daily(last_date, date,
            fields='pct_change')['pct_change']
        self.factor = change.groupby(level=1).std()

class FF3F(FactorVolatility):
    def __init__(self, period):
        name = 'ff3f_' + str(period)
        self.period = period
        super().__init__(name)

    def calculate(self, date):
        pass


if __name__ == "__main__":
    factor = Std(20)
    print(factor('20200106'))