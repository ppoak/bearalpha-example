import bearalpha as ba


class SMACrossStrategy(ba.Strategy):
    def __init__(self):
        sma5 = ba.indicators.SMA(period=5)
        sma10 = ba.indicators.SMA(period=10)
        self.buycross = ba.And(sma5(-1) <= sma10(-1), sma5 > sma10)
        self.sellcross = ba.And(sma5(-1) >= sma10(-1), sma5 < sma10)
    
    def next(self):
        if self.buycross[0]:
            self.order_target_percent(target=1)

        elif self.sellcross[0]:
            self.order_target_percent(target=0)


class TurtleStrategy(ba.Strategy):
    
    def __init__(self) -> None:
        self.atr = ba.indicators.ATR(period=14)
        self.unit = 0.1
        self.currentpos = 0
        self.order = None
        self.lastbuyprice = ba.inf
        self.alreadybuy = False
        high = ba.indicators.Highest(self.data.high, period=20)
        self.buysig = high(-1) <= self.data.close

    def next(self):
        if self.buysig[0] and not self.alreadybuy:
            self.order_target_percent(target=self.currentpos + self.unit)

        elif self.alreadybuy and self.data.close[0] >= self.lastbuyprice + self.atr[0]:
            self.order_target_percent(target=self.currentpos + self.unit)

    def notify_order(self, order):
        if order.status in [order.Created, order.Accepted, order.Submitted]:
            return
        elif order.status in [order.Completed]:
            self.log(f'Trade <{order.executed.size}> at <{order.executed.price}>')
            if order.isbuy():
                self.currentpos += self.unit
                self.lastbuyprice = order.executed.price
                self.alreadybuy = True
                if len(self.broker.pending) > 0:
                    # price = self.broker.pending[0].price + self.atr[0]
                    self.cancel(self.broker.pending[0])
                # else:
                price = order.executed.price - self.atr[0]
                self.sell(size=self.getposition().size, 
                    exectype=ba.Order.Stop, price=price)
            else:
                self.alreadybuy = False
                self.currentpos = 0

class BollingStrategy(ba.Strategy):
    def __init__(self):
        self.bollings = []
        for data in self.datas:
            self.bollings.append(ba.indicators.BollingerBands(data, period=20, devfactor=2))
    
    def next(self):
        for i, data in enumerate(self.datas):
            if data.close[0] >= self.bollings[i].bot[0] and data.close[-1] < self.bollings[i].bot[-1]:
                self.order_target_percent(data, target=0.50, name=data._name)
            elif data.close[0] <= self.bollings[i].top[0] and data.close[-1] > self.bollings[i].top[-1]:
                self.order_target_percent(data, target=0, name=data._name)
