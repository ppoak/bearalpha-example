from ..core import FactorBase


class FactorAlpha101(FactorBase):
    def __init__(self, name):
        super().__init__(name)
        self.klass = 'alpha101'


class Alphal001(FactorAlpha101):
    """Calculation: (rank(Ts_ArgMax(SignedPower(((returns < 0) ? stddev(returns, 20) : close), 2.), 5)) - 0.5)"""
    def __init__(self):
        super().__init__("alpha#001")
    
    def calculate(self, date):
        pass


class Alpha101(FactorAlpha101):
    """Calculation: ((close - open) / ((high - low) + .001))
    
    - image a K line, the formula mean the portion of lenght 
        the entity part to the whole K line 
    """
    def __init__(self):
        super().__init__('alpha#101')
    
    def calculate(self, date):
        prices = self.datasource.market_daily(date, date, 
            fields=['adjclose', 'adjopen', 'adjhigh', 'adjlow']).droplevel(0)
        self.factor = ((prices.adjclose - prices.adjopen) / (prices.adjhigh - prices.adjlow) + 0.001)


if __name__ == "__main__":
    import time
    start = time.time()
    factor = Alpha101()
    data = factor('2022-07-01')
    print(factor)
    data.printer.display(title='factor')
    print(f'time: {time.time() - start:.2f}s')
