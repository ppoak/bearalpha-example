import bearalpha as ba
from ..core import FactorBase

class FactorTechnical(FactorBase):
    def __init__(self, name):
        super().__init__(name)
        self.klass = 'technical'

class Macd(FactorTechnical):
    def __init__(self):
        super().__init__('macd')
    
    def calculate(self, date):
        self.factor = ba.Stock.intensity_trend(date, date,
            fields='macd_macd').droplevel(0)['macd_macd']


if __name__ == "__main__":
    import time
    factor = Macd()
    start = time.time()
    print(factor('20200106'))
    print(f'time: {time.time() - start:.2f}s')