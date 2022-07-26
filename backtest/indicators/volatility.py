import backtrader as bt


class ATRinc(bt.Indicator):
    lines = ('atrinc5', 'atrinc10')

    def __init__(self) -> None:
        atr = bt.indicators.ATR(period=14) 
        atrinc = (atr - atr(-1)) / atr(-1)
        self.lines.atrinc5 = bt.indicators.SMA(atrinc, period=10)
        self.lines.atrinc10 = bt.indicators.SMA(atrinc, period=60)
