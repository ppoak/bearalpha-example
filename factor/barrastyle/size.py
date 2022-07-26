import bearalpha as ba
from ..core import FactorBase

class FactorSize(FactorBase):
    def __init__(self, name):
        super().__init__(name)
        self.klass = 'size'

class Capital(FactorSize):
    def __init__(self):
        super().__init__('capital')
    
    def calculate(self, date):
        self.factor = ba.Stock.derivative_indicator(date, date,
            fields='s_val_mv').droplevel(0).s_val_mv

if __name__ == '__main__':
    factor = Capital()
    print(factor('20200106'))