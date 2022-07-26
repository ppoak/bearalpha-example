import bearalpha as ba
from ..indicators import *

class RelocateStrategy(ba.Strategy):

    def __init__(self) -> None:
        self.portfolio = {}

    def next(self):
        for d in self.datas:
            if d.position[0] != self.portfolio.get(d._name, 0):
                self.order_target_percent(d, target=d.position[0])
            self.portfolio[d._name] = d.position[0]
