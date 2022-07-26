import bearalpha as ba
from ..indicators import *



class GridStrategy(ba.Strategy):
    params = (('cashnum', 5),)
    
    def __init__(self) -> None:
        self.grids = Grid(period=20)
        self.levels = [self.grids.level1, self.grids.level2, self.grids.level3, self.grids.level4, self.grids.level5]
        self.grid = self.grids.grid
        self.pregrid = self.grids.grid(-1)
        self.griddiff = self.grid - self.pregrid
        self.cashes = [self.broker.getcash() / self.p.cashnum for _ in range(self.p.cashnum)]
        self.holds = []
    
    def notify_order(self, order: ba.Order):
        if order.status in [order.Created, order.Accepted, order.Submitted]:
            return
        elif order.status in [order.Completed]:
            self.log(f'Trade <{order.executed.size}> at <{order.executed.price}>')
            if order.isbuy():
                self.cashes.pop()
                self.holds.append(order.executed.size)
            else:
                self.holds.pop()
                self.cashes.append(-order.executed.price * order.executed.size)
        elif order.status in [order.Canceled, order.Margin, order.Rejected, order.Expired]:
            self.log(f'order failed to execute')

    def buygrid(self, grid: int):
        if self.cashes:
            if grid == 0:
                self.order = self.buy(size=self.cashes[-1] // self.data.low[0],
                    exectype=ba.Order.Limit, price=self.data.low[0])
            else:
                self.order = self.buy(size=self.cashes[-1] // self.levels[int(grid - 1)][0],
                    exectype=ba.Order.Limit, price=self.levels[int(grid - 1)][0])
        else:
            self.log(f'Grid drop, no cash to buy', hint='WARN')

    def sellgrid(self, grid: int):
        if self.holds:
            if grid == 4:
                self.order = self.sell(size=self.holds[-1], exectype=ba.Order.Limit, price=self.data.high[0])
            else:
                self.order = self.sell(size=self.holds[-1], exectype=ba.Order.Limit, price=self.levels[int(grid)][0])
        else:
            self.log(f'Grid raise, no holds to sell', hint='WARN')

    def nextstart(self):
        self.log(f'start with {self.grid[0]}')
        self.buygrid(self.grid[0])
    
    def next(self):
        if self.griddiff[0] < 0:
            if self.order.status not in [self.order.Canceled, self.order.Completed, self.order.Rejected, self.order.Expired]:
                self.cancel(self.order)
            self.buygrid(self.grid[0])
        elif self.griddiff[0] > 0:
            if self.order.status not in [self.order.Canceled, self.order.Completed, self.order.Rejected, self.order.Expired]:
                self.cancel(self.order)
            self.sellgrid(self.grid[0])

