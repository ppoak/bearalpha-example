import bearalpha as ba


class KShape(ba.Indicator):
    lines = ('hammer', 'hangingman', 'piercing', )
    plotinfo = dict(subplot=True)

    def __init__(self):
        self.lines.hammer = ba.talib.CDLHAMMER(self.data.open, 
            self.data.high, self.data.low, self.data.close)
        self.lines.hangingman = ba.talib.CDLHANGINGMAN(self.data.open,
            self.data.high, self.data.low, self.data.close)
        self.lines.piercing = ba.talib.CDLPIERCING(self.data.open,
            self.data.high, self.data.low, self.data.close)
