import backtrader as bt


class SMACombination(bt.Indicator):
    lines = ('sma5', 'sma10', 'sma20', 'sma60', 'sma120', 'sma250')
    plotinfo = dict(subplot=True)

    def __init__(self) -> None:
        self.lines.sma5 = bt.indicators.SMA(period=5)
        self.lines.sma10 = bt.indicators.SMA(period=10)
        self.lines.sma20 = bt.indicators.SMA(period=20)
        self.lines.sma60 = bt.indicators.SMA(period=60)
        self.lines.sma120 = bt.indicators.SMA(period=120)
        self.lines.sma250 = bt.indicators.SMA(period=250)
